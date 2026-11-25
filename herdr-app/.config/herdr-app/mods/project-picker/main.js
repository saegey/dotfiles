// Project picker: fuzzy-find a git repo under a configured folder, then focus
// the space already working in it or create one. Type to filter, ↑/↓ and
// Enter to go, ctrl+, for settings, Esc to leave (or go back).
//
//   config.js       settings (folder, depth, ignore list), in shared state
//   fuzzy.js        search
//   projects.js     scanning, and focusing/creating spaces
//   ui.js           picker view pieces
//   settings-ui.js  the settings page
//   main.js         state, keys, layout (this file)

import { View } from "gpui-kit";
import { v_flex, InputState, VirtualListScrollHandle } from "gpui-base";
import { theme, props, closeOverlay, pickFolder, focused, spaces, machines } from "herdr";
import { getConfig, updateConfig, resetConfig, DEPTH_RANGE } from "./config.js";
import { search } from "./fuzzy.js";
import { scanProjects, spacesByFolder, openProject } from "./projects.js";
import { header, machineBar, searchBox, message, resultsView, ROW_HEIGHT, LIST_HEIGHT } from "./ui.js";
import { settingsPage } from "./settings-ui.js";

/** What a scan depends on: when this changes, the results are stale. */
const scanKey = (machine) => {
  const { root, maxDepth, ignore } = getConfig(machine);
  return JSON.stringify([machine, root, maxDepth, ignore]);
};

/** The machine of the focused space: where the picker searches at first. */
const focusedMachine = () => {
  const id = focused()?.space;
  return spaces().find((s) => s.id === id)?.machine ?? null;
};

/** Machines the picker can search: this computer and every other known machine. */
const pickableMachines = () =>
  machines().filter((m) => !m.temporary).map((m) => ({ name: m.name ?? null, unavailable: m.layout === "unavailable" }));

export default class ProjectPicker extends View {
  init(_props, cx) {
    this.machine = focusedMachine(); // searched; null: this computer
    this.settingsMachine = this.machine; // whose settings the settings page edits
    this.projects = null; // null while scanning
    this.root = null; // absolute root on this.machine, once known
    this.error = null; // why the last scan failed
    this.scanned = null; // scanKey() of the last scan
    this.query = "";
    this.matches = { projects: null, query: null, list: [] }; // results() cache
    this.selected = 0;
    this.firstRow = 0; // first row in view, reported by the list
    this.listHeight = LIST_HEIGHT; // reported by the list once laid out
    this.page = "search"; // "search" | "settings"
    this.focus = cx.focus_handle();
    this.scroll = VirtualListScrollHandle.new();

    this.input = InputState.new({ placeholder: "Pick a project…" });
    this.input.on("change", (_e, cx) => {
      this.query = this.input.value();
      this.selected = 0;
      if (this.results().length) this.scroll.scroll_to_item(0);
      cx.notify();
    });
    this.input.on("submit", () => this.pick(this.results()[this.selected]));

    this.rootInput = InputState.new({ value: getConfig(this.settingsMachine).root, placeholder: "~" });
    this.rootInput.on("change", (_e, cx) => {
      const root = this.rootInput.value().trim();
      if (root) updateConfig({ root }, this.settingsMachine);
      cx.notify();
    });

    this.ignoreInput = InputState.new({ placeholder: "Folder name to ignore, e.g. dist" });
    this.ignoreInput.on("submit", (_e, cx) => this.addIgnore(cx));

    // Tab is the window's "next field" action and never reaches on_key_down, so
    // bind it to our own actions inside this view's key context.
    cx.bind_keys([
      { keystroke: "tab", action: "project-picker.next-machine", context: "ProjectPicker" },
      { keystroke: "shift-tab", action: "project-picker.prev-machine", context: "ProjectPicker" },
    ]);

    // The overlay takes focus as it opens, so claim it again once it has.
    this.input.focus();
    cx.timer.after(600, () => (this.page === "search" ? this.input : this.rootInput).focus());
    this.rescan(cx);
  }

  close() {
    this.scroll.release();
  }

  rescan(cx) {
    const machine = this.machine;
    const key = scanKey(machine);
    this.scanned = key;
    this.projects = null;
    this.root = null;
    this.error = null;
    cx.spawn(async (cx) => {
      try {
        const { projects, root } = await scanProjects(machine);
        if (this.scanned === key) { this.projects = projects; this.root = root; }
      } catch (err) {
        if (this.scanned === key) {
          this.projects = [];
          this.error = `Can't search ${machine ?? "this computer"}: ${String(err?.message ?? err).split("\n")[0]}`;
        }
      }
      cx.notify();
    });
  }

  /** Search another machine: its own root setting, its own results. The typed query stays. */
  selectMachine(machine, cx) {
    if (machine === this.machine) return;
    this.machine = machine;
    this.selected = 0;
    this.rescan(cx);
    cx.notify();
  }

  /** The projects matching the query, best first. Cached until either changes. */
  results() {
    const m = this.matches;
    if (m.projects !== this.projects || m.query !== this.query) {
      this.matches = { projects: this.projects, query: this.query, list: search(this.projects ?? [], this.query) };
    }
    return this.matches.list;
  }

  dismiss() {
    closeOverlay(props().overlay);
  }

  pick(project) {
    if (!project || this.root === null) return;
    this.dismiss();
    openProject(project, this.machine, this.root);
  }

  showPage(page, cx) {
    this.page = page;
    if (page === "search") {
      // Back from settings: scan again if the folder, depth or ignore list changed.
      if (this.scanned !== scanKey(this.machine)) this.rescan(cx);
      this.input.focus();
    } else {
      this.settingsMachine = this.machine;
      this.rootInput.set_value(getConfig(this.machine).root);
      this.rootInput.focus();
    }
    cx.notify();
  }

  // --- settings actions ---

  selectSettingsMachine(machine, cx) {
    this.settingsMachine = machine;
    this.rootInput.set_value(getConfig(machine).root);
    cx.notify();
  }

  async browse(cx) {
    const folder = await pickFolder({ prompt: "Projects folder" });
    if (!folder) return;
    this.rootInput.set_value(folder);
    updateConfig({ root: folder }, null);
    cx.notify();
  }

  stepDepth(delta, cx) {
    const { min, max } = DEPTH_RANGE;
    const depth = getConfig(this.settingsMachine).maxDepth + delta;
    updateConfig({ maxDepth: Math.max(min, Math.min(max, depth)) }, this.settingsMachine);
    cx.notify();
  }

  addIgnore(cx) {
    const name = this.ignoreInput.value().trim();
    const { ignore } = getConfig(this.settingsMachine);
    if (name && !ignore.includes(name)) updateConfig({ ignore: [...ignore, name] }, this.settingsMachine);
    this.ignoreInput.set_value("");
    cx.notify();
  }

  removeIgnore(name, cx) {
    updateConfig({ ignore: getConfig(this.settingsMachine).ignore.filter((n) => n !== name) }, this.settingsMachine);
    cx.notify();
  }

  reset(cx) {
    resetConfig(this.settingsMachine);
    this.rootInput.set_value(getConfig(this.settingsMachine).root);
    cx.notify();
  }

  // --- keys ---

  /** Move the selection by `delta` (wrapping) and scroll it into view. */
  move(delta) {
    const count = this.results().length;
    if (!count) return;
    const visibleRows = Math.max(1, Math.floor(this.listHeight / ROW_HEIGHT));
    this.selected = (this.selected + delta + count) % count;
    if (this.selected < this.firstRow) this.scroll.scroll_to_item(this.selected);
    else if (this.selected >= this.firstRow + visibleRows) this.scroll.scroll_to_item(this.selected - visibleRows + 1);
  }

  /** Switch to the next (or previous) machine, wrapping around. */
  cycleMachine(delta, cx) {
    const names = pickableMachines().map((m) => m.name);
    if (names.length < 2) return;
    const at = Math.max(0, names.indexOf(this.machine));
    this.selectMachine(names[(at + delta + names.length) % names.length], cx);
  }

  onKey(e, cx) {
    if (e.key === "escape") {
      if (this.page === "settings") this.showPage("search", cx);
      else this.dismiss();
    } else if (e.key === "," && e.modifiers.control) {
      this.showPage(this.page === "search" ? "settings" : "search", cx);
    } else if (this.page === "search" && (e.key === "down" || e.key === "up")) {
      this.move(e.key === "down" ? 1 : -1);
    } else return;
    cx.stop_propagation();
    cx.notify();
  }

  // --- views ---

  resultsList(t) {
    const results = this.results();
    if (this.projects === null) return message(t, "Scanning…");
    if (this.error) return message(t, this.error);
    if (!results.length) return message(t, "No git repository found");
    this.selected = Math.min(this.selected, results.length - 1);
    const open = spacesByFolder(this.machine);
    return resultsView(t, {
      results,
      selected: this.selected,
      isOpen: (project) => open.has(`${this.root}/${project}`),
      scroll: this.scroll,
      onRange: (range) => { this.firstRow = range.start; },
      onResize: (height, cx) => { if (height !== this.listHeight) { this.listHeight = height; cx.notify(); } },
      onPick: (project) => this.pick(project),
    });
  }

  render() {
    const t = theme();
    const settings = this.page === "settings";
    return v_flex()
      .id("project-picker")
      .key_context("ProjectPicker")
      .on_action("project-picker.next-machine", (_e, cx) => this.page === "search" && this.cycleMachine(1, cx))
      .on_action("project-picker.prev-machine", (_e, cx) => this.page === "search" && this.cycleMachine(-1, cx))
      .track_focus(this.focus)
      .size_full().p(18).gap(10)
      .bg(t.popover)
      .text_size(13)
      .on_key_down((e, cx) => this.onKey(e, cx))
      .child(header(t, settings ? "Settings" : "Projects", {
        label: settings ? "← Back" : "⚙ Settings",
        onClick: (_e, cx) => this.showPage(settings ? "search" : "settings", cx),
      }))
      .children(settings
        ? [settingsPage(t, {
            config: getConfig(this.settingsMachine),
            machineName: this.settingsMachine,
            machineTabs: machineBar(t, pickableMachines(), this.settingsMachine, (name, cx) => this.selectSettingsMachine(name, cx)),
            rootInput: this.rootInput,
            ignoreInput: this.ignoreInput,
            onBrowse: (_e, cx) => this.browse(cx),
            onStepDepth: (delta, cx) => this.stepDepth(delta, cx),
            onAddIgnore: (_e, cx) => this.addIgnore(cx),
            onRemoveIgnore: (name, cx) => this.removeIgnore(name, cx),
            onReset: (_e, cx) => this.reset(cx),
          })]
        : [machineBar(t, pickableMachines(), this.machine, (name, cx) => this.selectMachine(name, cx)),
           searchBox(t, this.input), this.resultsList(t)]);
  }
}
