export const OWNER = "dotfiles.gui-music";
export const OVERLAY = "dotfiles.music.overlay";

export function statusText(value) {
  return String(value || "").replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, "")
    .replace(/[\x00-\x1f\x7f-\x9f]/g, " ").replace(/\s+/g, " ").trim();
}

// Input comes from hc ls --label OWNER=appHome. Its compact JSON deliberately
// omits labels, so ownership is established by the query rather than these rows.
export function musicTerminal(terminals) {
  const matches = terminals.filter(t => t.state === "live"
    && typeof t.address === "string" && !t.address.includes("/"));
  if (matches.length > 1) throw new Error("Multiple GUI music sessions found; refusing to choose one.");
  return matches[0]?.address || null;
}

// Replace only this app's remote-player UI; the Lounge player runs on the server.
export async function freshPlayer(runCore, owner, home) {
  const find = async () => {
    const result = await runCore(["ls", "--json", "--label", `${OWNER}=${owner}`]);
    if (result.code !== 0) throw new Error("Cannot inspect the GUI music session in Herdr Core.");
    return musicTerminal(JSON.parse(result.stdout).terminals || []);
  };
  const previous = await find();
  if (previous) {
    const result = await runCore(["kill", previous, "--json"]);
    if (result.code !== 0) throw new Error("Could not close the previous GrooveNet UI; no new session started.");
  }
  // No fixed name: finished core terminals may retain their old names.
  const result = await runCore(["run", "--json", "--bg", "--no-parent", "--no-notify",
    "--label", `${OWNER}=${owner}`, "--cwd", home, "--", `${home}/.local/bin/herdr-music`, "--player"]);
  if (result.code !== 0) throw new Error("Could not start the GrooveNet UI. Check Herdr Core and the launcher.");
  const terminal = await find();
  if (!terminal) throw new Error("The GrooveNet UI exited during startup. Check the launcher.");
  return terminal;
}
