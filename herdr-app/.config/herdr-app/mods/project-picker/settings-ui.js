// The settings page: root folder, scan depth, ignored folders.

import { div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { DEPTH_RANGE } from "./config.js";
import { inputBox } from "./ui.js";

function field(t, label, hint, control) {
  return v_flex().gap(4)
    .child(div().font_semibold().text_color(t.foreground).child(label))
    .child(div().text_size(11).text_color(t.dim).child(hint))
    .child(control);
}

function button(t, id, label, onClick, { disabled = false } = {}) {
  return h_flex().id(id)
    .h(30).px(12).items_center().justify_center().rounded(7)
    .border_1().border_color(t.border).text_color(disabled ? t.dim : t.foreground)
    .when(!disabled, (el) => el.cursor_pointer().hover((s) => s.bg(t.hover)).on_click(onClick))
    .child(label);
}

function depthStepper(t, value, onStep) {
  const { min, max } = DEPTH_RANGE;
  return h_flex().gap(8).items_center()
    .child(button(t, "depth-dec", "−", (_e, cx) => onStep(-1, cx), { disabled: value <= min }))
    .child(div().w(32).text_color(t.foreground).child(String(value)).text_center())
    .child(button(t, "depth-inc", "+", (_e, cx) => onStep(1, cx), { disabled: value >= max }))
    .child(div().text_size(11).text_color(t.dim).child(`${min}–${max}`));
}

function chip(t, name, onRemove) {
  return h_flex().id(`ignore-${name}`)
    .h(26).pl(10).pr(6).gap(6).items_center().rounded(13).bg(t.raised).text_size(12).text_color(t.foreground)
    .child(name)
    .child(div().id(`ignore-rm-${name}`).px(4).text_color(t.dim).cursor_pointer()
      .hover((s) => s.text_color(t.foreground)).on_click(onRemove).child("×"));
}

function ignoreList(t, { ignore, ignoreInput, onAddIgnore, onRemoveIgnore }) {
  return v_flex().gap(8)
    .child(h_flex().gap(8).items_center()
      .child(inputBox(t, ignoreInput))
      .child(button(t, "ignore-add", "Add", onAddIgnore)))
    .child(h_flex().flex_wrap().gap(6).children(
      ignore.length
        ? ignore.map((name) => chip(t, name, (_e, cx) => onRemoveIgnore(name, cx)))
        : [div().text_size(11).text_color(t.dim).child("Nothing ignored")]));
}

export function settingsPage(t, { config, machineName, machineTabs, rootInput, ignoreInput, onBrowse, onStepDepth, onAddIgnore, onRemoveIgnore, onReset }) {
  const where = machineName ?? "this computer";
  // The scrollbar sits in the right gutter (pr), not over the fields.
  return div().id("settings-scroll").flex_1().min_h_0().overflow_y_scrollbar().child(v_flex().gap(14).pr(16)
    .child(machineTabs)
    .child(field(t, "Projects folder", `Scanned for git repositories on ${where}. ~ is its home folder.`,
      h_flex().gap(8).items_center()
        .child(inputBox(t, rootInput))
        // The system folder picker only sees this computer.
        .when(machineName === null, (el) => el.child(button(t, "browse", "Browse…", onBrowse)))))
    .child(field(t, "Scan depth", "How many folders below the root a repository may be.",
      depthStepper(t, config.maxDepth, onStepDepth)))
    .child(field(t, "Ignored folders", "Skipped while scanning: a folder name (dist, *-cache) or a path (~/dev/archive). Enter adds.",
      ignoreList(t, { ignore: config.ignore, ignoreInput, onAddIgnore, onRemoveIgnore })))
    .child(h_flex().child(button(t, "reset", `Reset ${where} to defaults`, onReset))));
}
