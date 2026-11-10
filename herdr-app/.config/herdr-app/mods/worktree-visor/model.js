// Presentation only. The existing Python collector remains shared with the terminal visor.
import { URL } from "url";

export function safeUrl(value) {
  if (typeof value !== "string" || /[\s\x00-\x1f\x7f\\]/.test(value)) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) && url.hostname && !url.username && !url.password ? value : null;
  } catch { return null; }
}

export function targetFor(focus, spaces) {
  const space = spaces.find(s => s.id === focus?.space);
  return { cwd: focus?.cwd || space?.folder || null, machine: space?.machine ?? null };
}

export function tone(status) {
  const value = String(status || "").toLowerCase().replaceAll("_", " ");
  if (["failure", "failed", "error", "timed out", "action required", "changes requested"].includes(value)) return "error";
  if (["success", "approved", "merged", "completed"].includes(value)) return "success";
  if (["pending", "queued", "in progress", "waiting", "requested", "review required", "draft", "cancelled", "stale"].includes(value)) return "warning";
  return "text";
}

export function rowsFor(data) {
  const rows = [];
  const add = (text, url, tone = "text") => rows.push({ text: String(text || ""), url: safeUrl(url), tone });
  const section = text => rows.push({ text, heading: true });
  const empty = (error, fallback) => add(error || fallback, null, error ? "warning" : "muted");
  section("App links");
  for (const app of data.apps || []) add(`${app.label}  ·  ${app.url}`, app.url);
  if (!data.apps?.length) empty(null, "No recorded app URLs for this checkout. Run make setup in the app repo to create them.");
  const issues = data.linear?.issue ? [data.linear.issue] : data.github_issues?.issues || [];
  section(data.linear?.issue || !issues.length && data.ticket ? "Linear" : "GitHub issues");
  for (const issue of issues) {
    add(`${issue.identifier}  ·  ${issue.state?.name || ""}`, issue.url);
    add(issue.title);
  }
  if (!issues.length) empty(data.github_issues?.error || data.linear?.error, "No issue found. Link an issue to the PR or use an issue-123 branch name.");
  else if (data.github_issues?.error) empty(data.github_issues.error);
  section("GitHub pull request");
  const pr = data.github?.pr;
  if (pr) {
    const state = pr.isDraft ? "Draft" : pr.state;
    add(`#${pr.number}  ·  ${state || ""}  ·  ${pr.reviewDecision || ""}`, pr.url, tone(pr.reviewDecision || state));
    add(pr.title);
    if (pr.headRefOid !== data.head) add("PR head differs from this checkout; Actions below are for local HEAD.", null, "warning");
    if (pr.statusCheckRollup?.length) add("PR head checks", null, "muted");
    for (const check of pr.statusCheckRollup || []) {
      const status = check.conclusion || check.state || check.status;
      add(`${status || ""}  ·  ${check.name || check.context || ""}`, check.detailsUrl || check.targetUrl, tone(status));
    }
  } else empty(data.github?.error, "No PR found for this branch.");
  section(`GitHub Actions · checkout ${(data.head || "").slice(0, 8)}`);
  for (const run of data.actions?.runs || []) {
    const status = run.conclusion || run.status;
    add(`${status}  ·  ${run.workflowName} (${run.event})`, run.url, tone(status));
  }
  if (!data.actions?.runs?.length) empty(data.actions?.error, "No Actions runs for this commit; it may not be pushed yet.");
  section("Dev stack");
  for (const project of data.stacks?.projects || []) {
    add(`${project.name}  ·  ${project.running}/${project.total} running  ·  ${project.unhealthy} unhealthy`, null,
      project.unhealthy ? "error" : project.running === project.total ? "success" : "warning");
  }
  if (data.stacks?.error || !data.stacks?.projects?.length) empty(data.stacks?.error, "No existing dev-stack containers for this checkout.");
  for (const issue of issues) {
    if (!issue.description) continue;
    section(`${issue.identifier} description`);
    rows.push({ text: issue.description.slice(0, 6000), markdown: true });
  }
  return rows;
}
