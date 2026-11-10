export const clean = value => typeof value === "string" ? value.replace(/[\x00-\x1f\x7f]/g, " ").replace(/\s+/g, " ").trim().slice(0, 240) : "";

export function reviewFor(records, g, machine) {
  if (machine || !g?.top) return null;
  const record = records?.[g.top];
  return record && record.branch === g.branch && Number.isInteger(record.pr) && record.pr > 0 ? record : null;
}

// Fold the presentation after ordering; never remove or move real spaces.
export function foldRows(rows, folded) {
  const groups = [];
  for (const row of rows) {
    const parent = groups[groups.length - 1];
    if (row.tree && parent?.g?.repo === row.g?.repo) parent.children.push(row);
    else groups.push({ ...row, children: [] });
  }
  return groups.flatMap(parent => {
    const closed = parent.children.length > 0 && folded.has(parent.g.repo);
    return [{ ...parent, closed }, ...(closed ? [] : parent.children)];
  });
}
export function ticketFor(value) {
  const ticket = String(value ?? "").match(/(?:^|[^A-Za-z0-9])([A-Za-z][A-Za-z0-9]*-[0-9]+)(?![0-9])/)?.[1]?.toUpperCase();
  return ticket && !/^(PR|ISSUE)-/.test(ticket) ? ticket : null;
}

export function repoPath(g, fallback) {
  try {
    const [, common] = JSON.parse(g.repo);
    return common.endsWith("/.git") ? common.slice(0, -5) : common;
  } catch { return fallback; }
}

export function iconFor(config, machine, path, userHome) {
  return (Array.isArray(config?.repos) ? config.repos : []).find(entry =>
    entry && (entry.machine ?? null) === (machine ?? null) && typeof entry.path === "string" &&
    entry.path.replace(/^~(?=\/|$)/, userHome).replace(/\/+$/, "") === path?.replace(/\/+$/, ""))?.icon ?? null;
}

export function badgeFor(snapshot, checkout, repoName) {
  const projects = (snapshot?.projects ?? []).filter(p => p.checkout === checkout);
  if (!projects.length && repoName !== "skysafe-cloud") return null;
  if (!snapshot || snapshot.error) return { text: "[?]", tone: "dim", tip: snapshot?.error || "Checking Docker…" };
  const running = projects.reduce((n, p) => n + (Number(p.running) || 0), 0);
  const total = projects.reduce((n, p) => n + (Number(p.total) || 0), 0);
  const unhealthy = projects.reduce((n, p) => n + (Number(p.unhealthy) || 0), 0);
  const starting = projects.some(p => p.starting > 0);
  return { text: `[${running}]`, tone: unhealthy ? "ansi1" : starting || running < total ? "ansi3" : running ? "ansi2" : "dim",
    tip: `${running}/${total} dev-stack containers running${unhealthy ? ` · ${unhealthy} unhealthy` : ""}${starting ? " · starting" : ""}` };
}
