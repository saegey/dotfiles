export const OWNER = "dotfiles.gui-music";
export const OVERLAY = "dotfiles.music.overlay";

export function statusText(value) {
  return String(value || "").replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, "")
    .replace(/[\x00-\x1f\x7f-\x9f]/g, " ").replace(/\s+/g, " ").trim();
}

export function playerName(owner) {
  let hash = 2166136261;
  for (let i = 0; i < owner.length; i++) hash = Math.imul(hash ^ owner.charCodeAt(i), 16777619);
  return `gui-music-${(hash >>> 0).toString(16)}`;
}

// Input comes from hc ls --label OWNER=appHome. Its compact JSON deliberately
// omits labels, so ownership is established by the query rather than these rows.
export function musicTerminal(terminals) {
  const matches = terminals.filter(t => t.state === "live"
    && typeof t.address === "string" && !t.address.includes("/"));
  if (matches.length > 1) throw new Error("Multiple GUI music sessions found; refusing to choose one.");
  return matches[0]?.address || null;
}
