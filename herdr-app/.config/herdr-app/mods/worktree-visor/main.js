import { View, div } from "gpui-kit";
import { v_flex, h_flex, ScrollHandle, TextView } from "gpui-base";
import { focused, spaces, exec, props, closeOverlay, theme } from "herdr";
import { rowsFor, safeUrl, targetFor } from "./model.js";

export default class WorktreeVisor extends View {
  init(_props, cx) {
    // Freeze the repo for this opening; an in-flight response must never change targets.
    this.target = targetFor(focused(), spaces());
    this.data = null;
    this.error = null;
    this.loading = false;
    this.selected = 0;
    this.handle = cx.focus_handle();
    this.scroll = ScrollHandle.new();
    this.handle.focus();
    cx.timer.after(50, () => this.handle.focus());
    this.refresh(cx);
    cx.timer.every(15000, cx => this.refresh(cx));
  }

  refresh(cx) {
    if (this.loading) return;
    if (!this.target.cwd) {
      this.error = "Open the visor from a repository terminal.";
      cx.notify();
      return;
    }
    this.loading = true;
    cx.notify();
    cx.spawn(async cx => {
      try {
        // Pass the folder as an argv value, never as shell source. The helper must
        // exist on the selected machine; no fallback to a different local repo.
        const result = await exec("bash", ["-c",
          'export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"; exec "$HOME/.local/bin/herdr-worktree-visor" --json --cwd "$1"',
          "worktree-visor", this.target.cwd], { cwd: this.target.cwd, on: this.target.machine, timeout: 120000 });
        if (result.code !== 0) throw new Error(result.stderr.trim() || result.stdout.trim() || `Collector exited ${result.code}`);
        const data = JSON.parse(result.stdout);
        if (!data || typeof data.directory !== "string" || typeof data.head !== "string") throw new Error("Invalid visor response");
        this.data = data;
        this.error = null;
      } catch (error) {
        this.error = String(error.message || error);
      }
      this.loading = false;
      cx.notify();
    });
  }

  dismiss() { closeOverlay(props().overlay); }

  close(_cx) { this.scroll?.release(); }

  button(id, label, action) {
    const t = theme();
    return div().id(id).px(10).py(5).rounded(6).text_color(t.muted)
      .cursor_pointer().hover(s => s.bg(t.hover).text_color(t.foreground))
      .on_click(action).child(label);
  }

  render(cx) {
    const t = theme();
    const rows = this.data ? rowsFor(this.data) : [];
    const links = rows.map((row, index) => ({ ...row, index })).filter(row => row.url);
    this.selected = Math.min(this.selected, Math.max(0, links.length - 1));
    const selected = links[this.selected];
    const colors = { error: t.blocked, warning: t.working, success: t.idle, muted: t.muted, text: t.foreground };
    return v_flex().id("worktree-visor").track_focus(this.handle).size_full().min_h(0)
      .p(20).gap(12).bg(t.popover).text_size(13).text_color(t.foreground)
      .on_key_down((event, cx) => {
        const key = event.keystroke;
        if (key === "escape" || key === "q") { cx.stop_propagation(); this.dismiss(); }
        else if (key === "r") { cx.stop_propagation(); this.refresh(cx); }
        else if (["down", "j", "up", "k"].includes(key) && links.length) {
          const delta = key === "down" || key === "j" ? 1 : -1;
          this.selected = (this.selected + delta + links.length) % links.length;
          this.scroll.scroll_to_item(links[this.selected].index);
          cx.stop_propagation(); cx.notify();
        } else if (key === "enter" && selected) { cx.stop_propagation(); cx.open_url(selected.url); }
      })
      .child(h_flex().items_center().gap(8)
        .child(div().flex_1().text_size(19).font_semibold().child("Worktree visor"))
        .child(this.button("visor-refresh", this.loading ? "Refreshing…" : "Refresh · R", (_e, cx) => this.refresh(cx)))
        .child(this.button("visor-close", "Close · Esc", () => this.dismiss())))
      .child(div().text_color(t.muted).child(`${this.target.machine ? this.target.machine + ":" : ""}${this.data?.directory || this.target.cwd || "No repository"}`))
      .child(div().text_color(t.dim).child(this.data
        ? `${this.data.branch || "Detached HEAD"}  ·  ${this.data.head.slice(0, 8)}  ·  Updated ${this.data.updated}`
        : this.loading ? "Loading ticket, pull request, Actions and dev stack…" : ""))
      .when(Boolean(this.error), el => el.child(div().text_color(t.blocked).child(`${this.data ? "Refresh failed; showing previous results. " : ""}${this.error}`)))
      .child(v_flex().id("visor-content").flex_1().min_h(0).overflow_y_scrollbar().track_scroll(this.scroll).gap(5)
        .children(rows.map((row, index) => {
          if (row.heading) return div().mt(14).mb(3).font_semibold().text_color(t.accent).child(row.text);
          if (row.markdown) return div().child(TextView.markdown(`visor-description-${index}`, row.text)
            .selectable(true).on_link_click((url, cx) => { if (safeUrl(url)) cx.open_url(url); }));
          return div().id(`visor-row-${index}`).px(8).py(5).rounded(5)
            .text_color(colors[row.tone] || t.foreground)
            .when(Boolean(row.url), el => el.cursor_pointer().hover(s => s.bg(t.hover))
              .when(selected?.index === index, el => el.bg(t.selected))
              .on_click((_e, cx) => cx.open_url(row.url)))
            .child(row.text);
        })))
      .child(div().text_size(11).text_color(t.dim).child("↑/↓ or J/K select links · Enter opens · R refreshes · Esc closes · Refreshes every 15 seconds"));
  }
}
