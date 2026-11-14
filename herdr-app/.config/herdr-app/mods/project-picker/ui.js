// Stateless view pieces: each takes the theme and data, returns an element.

import { div, svg } from "gpui-kit";
import { v_flex, h_flex, Input, Scrollbar, v_virtual_list } from "gpui-base";

export const ROW_HEIGHT = 34; // the 32px row plus 1px of air above and below
export const LIST_HEIGHT = 300; // first guess, until the list reports the height it really got

/** Title bar. `action` is an optional { label, onClick } button on the right. */
export function header(t, title, action) {
  return h_flex()
    .items_center().gap(10)
    .child(div().flex_1().text_size(15).font_semibold().text_color(t.foreground).child(title))
    .when(action, (el) => el.child(
      div().id("header-action").text_size(12).text_color(t.muted).cursor_pointer()
        .hover((s) => s.text_color(t.foreground)).on_click(action.onClick).child(action.label)))
    .child(div().text_size(11).text_color(t.dim).child("Esc"));
}

/**
 * One chip per machine, shown only when there's a choice.
 * `machines`: [{ name, unavailable }], name null for this computer.
 */
export function machineBar(t, machines, current, onSelect) {
  if (machines.length < 2) return div();
  return h_flex().flex_wrap().gap(6).children(machines.map((m) => {
    const active = m.name === current;
    return h_flex().id(`machine-${m.name ?? "local"}`)
      .h(24).px(10).items_center().rounded(12).text_size(12).cursor_pointer()
      .border_1().border_color(active ? t.accent : t.border)
      .text_color(active ? t.foreground : m.unavailable ? t.dim : t.muted)
      .hover((s) => s.bg(t.hover))
      .on_click((_e, cx) => onSelect(m.name, cx))
      .child(m.name ?? "This computer");
  }));
}

/** A text input in a bordered box. */
export function inputBox(t, input) {
  return h_flex()
    .h(34).flex_1().px(10).items_center().rounded(8)
    .border_1().border_color(t.border).bg(t.background)
    .child(Input.new(input).flex_1().h_full().text_size(12.8).text_color(t.foreground));
}

export function searchBox(t, input) {
  return h_flex()
    .h(36).flex_none().px(10).gap(8).items_center()
    .rounded(9).border_1().border_color(t.accent).bg(t.background)
    .child(svg("mods/project-picker/search.svg").size(15).text_color(t.dim))
    .child(Input.new(input).flex_1().h_full().text_size(12.8).text_color(t.foreground));
}

export function message(t, text) {
  return div().px(10).py(8).text_color(t.dim).child(text);
}

/** One result: the project path and whether it's already open. */
function projectRow(t, { project, isOpen, selected }) {
  return v_flex().h(ROW_HEIGHT).justify_center().child(
    h_flex()
      .px(10).h(32).gap(8).items_center().rounded(7).cursor_pointer()
      .when(selected, (el) => el.bg(t.hover))
      .child(div().flex_1().truncate().text_color(t.foreground).child(project))
      .child(div().text_size(11).text_color(isOpen ? t.accent : t.dim).child(isOpen ? "open" : "new")));
}

/**
 * The results in a native virtual list: only the rows in view are built.
 * `scroll` is the list's VirtualListScrollHandle, `onRange(range)` reports
 * which rows are showing, `onResize(height)` its real height, and a click on a row calls `onPick(project)`.
 */
export function resultsView(t, { results, selected, isOpen, scroll, onRange, onResize, onPick }) {
  return v_flex().id("project-list").relative().flex_1().min_h_0()
    .on_size_change((size, cx) => onResize(size.height, cx))
    .child(v_virtual_list("project-results", results.length, ROW_HEIGHT, (i) => results[i], (range) => {
      onRange(range);
      return results.slice(range.start, range.end).map((project, k) =>
        projectRow(t, { project, isOpen: isOpen(project), selected: range.start + k === selected }));
    }).track_scroll(scroll).on_item_click((project) => onPick(project)).size_full())
    .child(Scrollbar.vertical("project-results").viewport_from_layout().absolute().inset_0());
}
