// Finding projects and opening them. A project is a path relative to the
// root ("opensource/cmux"). `machine` is a machine name, or null for this
// computer; everything runs there.

import { exec, home, panes, spaces, run } from "herdr";
import { getConfig, expandHome } from "./config.js";

const homes = new Map(); // machine name -> home folder, once known

/** The home folder of `machine`. Throws if the machine can't be reached. */
async function homeOf(machine) {
  if (machine === null) return home();
  if (!homes.has(machine)) {
    const { stdout } = await exec("sh", ["-c", 'printf %s "$HOME"'], { on: machine });
    if (!stdout.trim()) throw new Error(`No home folder on ${machine}`);
    homes.set(machine, stdout.trim());
  }
  return homes.get(machine);
}

/**
 * One find(1) test per ignore entry: a plain name matches any folder with that
 * name; an entry with a "/" (~ allowed) is a path, kept only if it is inside the root.
 */
function ignoreTests(ignore, root, homeFolder) {
  return ignore.flatMap((entry) => {
    if (!entry.includes("/") && !entry.startsWith("~")) return [["-name", entry]];
    const abs = expandHome(entry, homeFolder).replace(/\/+$/, "");
    return abs.startsWith(`${root}/`) ? [["-path", `.${abs.slice(root.length)}`]] : [];
  });
}

/** find(1) arguments that skip ignored folders and print each `.git` folder (worktrees have a `.git` file, so they're not listed). */
function findArgs({ maxDepth, ignore }, root, homeFolder) {
  const skip = ignoreTests(ignore, root, homeFolder).flatMap((test, i) => (i ? ["-o", ...test] : test));
  return [
    ".", "-maxdepth", String(maxDepth),
    ...(skip.length ? ["(", ...skip, ")", "-prune", "-o"] : []),
    "-type", "d", "-name", ".git", "-prune", "-print",
  ];
}

/**
 * Every git repository under the configured root on `machine`, sorted, with
 * that root's absolute path. Throws if the machine can't be reached.
 */
export async function scanProjects(machine) {
  const homeFolder = await homeOf(machine);
  const config = getConfig(machine);
  const root = expandHome(config.root, homeFolder);
  const { stdout } = await exec("find", findArgs(config, root, homeFolder), { cwd: root, on: machine ?? undefined });
  const projects = stdout
    .split("\n")
    .map((path) => path.replace(/^\.\//, "").replace(/(^|\/)\.git$/, ""))
    .filter(Boolean)
    .sort();
  return { projects, root };
}

/** folder -> id of the space on `machine` working in it (its own folder, or one of its terminals'). */
export function spacesByFolder(machine) {
  const here = spaces().filter((s) => (s.machine ?? null) === machine);
  const ids = new Set(here.map((s) => s.id));
  const byFolder = new Map();
  for (const s of here) if (s.folder) byFolder.set(s.folder, s.id);
  for (const p of panes()) if (ids.has(p.space) && p.cwd && !byFolder.has(p.cwd)) byFolder.set(p.cwd, p.space);
  return byFolder;
}

/** Focus the project's space, or create one on `machine`. */
export function openProject(project, machine, root) {
  const folder = `${root}/${project}`;
  const space = spacesByFolder(machine).get(folder);
  if (space) run("space.select", { id: space });
  else run("space.new", { name: project.split("/").pop(), folder, machine: machine ?? "" });
}
