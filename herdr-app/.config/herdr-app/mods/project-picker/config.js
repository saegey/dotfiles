// User settings, edited from the picker's settings page (gear, or ctrl+,).
// Kept in Herdr's shared state, so they survive restarts.
//
// Every machine has its own root folder, scan depth and ignore list.

import { shared, setShared } from "herdr";

const KEY = "project-picker.config";

/** Allowed range of the scan depth. */
export const DEPTH_RANGE = { min: 1, max: 8 };

const defaults = () => ({
  root: "~", // folder scanned for git repositories
  maxDepth: 4, // how deep below root a `.git` may sit
  ignore: ["node_modules", "Library", ".Trash", ".cache"], // folder names or paths never entered
});

/** `raw` with anything missing or invalid replaced by its default. */
function clean(raw) {
  const d = defaults();
  const c = { ...d, ...raw };
  return {
    root: typeof c.root === "string" && c.root.trim() ? c.root.trim() : d.root,
    maxDepth: Math.max(DEPTH_RANGE.min, Math.min(DEPTH_RANGE.max, Number(c.maxDepth) || d.maxDepth)),
    ignore: Array.isArray(c.ignore) ? c.ignore.filter((n) => typeof n === "string" && n.trim()) : d.ignore,
  };
}

// Stored as { ...this computer's settings, machines: { <name>: settings } }.
const state = () => shared(KEY) ?? {};

/** The settings of `machine` (null: this computer). */
export function getConfig(machine = null) {
  const s = state();
  return clean(machine === null ? s : s.machines?.[machine]);
}

function save(machine, config) {
  const s = state();
  setShared(KEY, machine === null ? { ...s, ...config } : { ...s, machines: { ...s.machines, [machine]: config } });
}

/** Save `patch` into the settings of `machine` (null: this computer). */
export function updateConfig(patch, machine = null) {
  save(machine, clean({ ...getConfig(machine), ...patch }));
}

/** Back to the defaults for `machine` (null: this computer). */
export function resetConfig(machine = null) {
  save(machine, defaults());
}

/** `path` with a leading ~ replaced by `homeFolder`. */
export function expandHome(path, homeFolder) {
  return path === "~" ? homeFolder : path.startsWith("~/") ? `${homeFolder}/${path.slice(2)}` : path;
}
