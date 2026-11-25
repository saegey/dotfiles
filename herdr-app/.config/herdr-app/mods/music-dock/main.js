import { View, div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { appHome, home, exec, hc, focused, theme, props, run, openOverlay, closeOverlay,
  nextCommand, shared, setShared, notify, checking } from "herdr";
import { OVERLAY, statusText, freshPlayer } from "./model.js";

export default class MusicDock extends View {
  init(_initial, cx) {
    this.status = "♫ Lounge · loading…";
    if (checking()) return;
    this.launcher = props()?.overlay;
    this.polling = false;
    this.opening = false;
    this.owner = appHome();
    // mod.open can launch the player even when the status strip is hidden.
    if (this.launcher) { this.toggle(cx); return; }
    // The layout owns the controller, not the player. Never start audio/UI on load.
    this.refresh(cx);
    cx.timer.every(2000, cx => this.refresh(cx));
    cx.spawn(async cx => {
      for (;;) {
        const command = await nextCommand();
        if (command === "toggle") this.toggle(cx);
      }
    });
  }

  refresh(cx) {
    if (this.polling) return;
    this.polling = true;
    cx.spawn(async cx => {
      let text = "♫ Lounge · idle or unavailable";
      try {
        const result = await exec("bash", ["-c", 'exec "$HOME/.local/bin/herdr-music" --status'], { timeout: 8000 });
        if (result.code === 0) text = statusText(result.stdout) || text;
        else text = "♫ Lounge · launcher unavailable";
      } catch { text = "♫ Lounge · status unavailable"; }
      this.polling = false;
      if (text !== this.status) { this.status = text; cx.notify(); }
    });
  }

  hide() {
    const overlay = shared(OVERLAY);
    if (!overlay) return;
    setShared(OVERLAY, null);
    closeOverlay(overlay.id);
  }

  toggle(cx) {
    if (shared(OVERLAY)) {
      this.hide();
      if (this.launcher) closeOverlay(this.launcher);
      return;
    }
    if (this.opening) return;
    this.opening = true;
    const context = focused();
    cx.spawn(async cx => {
      try {
        const terminal = await freshPlayer(hc, this.owner, home());
        // Navigation while starting must not pull the person back to another tab.
        if (context?.space !== focused()?.space || context?.tab !== focused()?.tab) return;
        // Closing a dialog also dismisses overlays above it. Remove the loading
        // dialog before opening the player, rather than closing it afterwards.
        if (this.launcher) {
          this.launcherClosed = true;
          closeOverlay(this.launcher);
        }
        const id = openOverlay({ kind: "dialog", modal: true, width: 0.9, height: 0.85,
          layout: { id: "music-window", type: "column", children: [
            { id: "music-header", type: "block", size: { px: 40 },
              content: { mod: "music-header", props: { terminal } } },
            { id: "music-player", type: "block", content: { terminal } },
          ] } });
        setShared(OVERLAY, { id, terminal, space: context?.space, tab: context?.tab });
      } catch (error) {
        notify({ title: "Lounge music", body: String(error.message || error), level: "error" });
      } finally {
        this.opening = false;
        if (this.launcher) {
          if (!this.launcherClosed) closeOverlay(this.launcher);
        } else cx.notify();
      }
    });
  }

  close() {
    if (!this.launcher) this.hide();
    // Hiding, layout switches and app quit leave the core terminal and playback alone.
  }

  render(cx) {
    const t = theme();
    if (this.launcher) {
      return div().p(16).text_color(t.foreground).child("Opening Lounge…");
    }
    const overlay = shared(OVERLAY), context = focused();
    if (overlay && (overlay.space !== context?.space || overlay.tab !== context?.tab)) this.hide();
    return h_flex().id("music-status").size_full().min_w(0).px(12).items_center()
      .bg(t.chrome).border_b(1).border_color(t.border).text_size(12).text_color(t.muted)
      .cursor_pointer().hover(s => s.bg(t.hover).text_color(t.foreground))
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
      .on_click((_e, cx) => this.toggle(cx))
      .child(div().min_w(0).truncate().child(this.opening ? "♫ Lounge · opening…" : this.status));
  }
}
