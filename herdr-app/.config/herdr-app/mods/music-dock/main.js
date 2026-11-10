import { View, div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { appHome, home, exec, hc, focused, theme, props, run, openOverlay, closeOverlay,
  nextCommand, shared, setShared, notify } from "herdr";
import { OWNER, OVERLAY, statusText, playerName, musicTerminal } from "./model.js";

export default class MusicDock extends View {
  init(_initial, cx) {
    this.header = Boolean(props()?.header);
    if (this.header) return;
    this.status = "♫ Lounge · loading…";
    this.polling = false;
    this.opening = false;
    this.owner = appHome();
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

  async findPlayer() {
    const result = await hc(["ls", "--json", "--label", `${OWNER}=${this.owner}`]);
    if (result.code !== 0) throw new Error("Cannot inspect the GUI music session in Herdr Core.");
    return musicTerminal(JSON.parse(result.stdout).terminals || []);
  }

  toggle(cx) {
    if (shared(OVERLAY)) { this.hide(); return; }
    if (this.opening) return;
    this.opening = true;
    const context = focused();
    cx.spawn(async cx => {
      try {
        let terminal = await this.findPlayer();
        if (!terminal) {
          // The unique name prevents parallel screens from starting duplicate players.
          // No herdr.space/tab labels: this UI lives in an overlay, not a work tab.
          const result = await hc(["run", "--json", "--bg", "--no-parent", "--no-notify",
            "--name", playerName(this.owner), "--label", `${OWNER}=${this.owner}`,
            "--cwd", home(), "--", `${home()}/.local/bin/herdr-music`, "--player"]);
          terminal = await this.findPlayer();
          if (!terminal) throw new Error(result.code === 0
            ? "The music player exited during startup. Check the GrooveNet launcher."
            : "Could not start the GUI music player. Check Herdr Core and the GrooveNet launcher.");
        }
        // Navigation while starting must not pull the person back to another tab.
        if (context?.space !== focused()?.space || context?.tab !== focused()?.tab) return;
        const id = openOverlay({ kind: "dialog", modal: true, width: 0.9, height: 0.85,
          layout: { id: "music-window", type: "column", children: [
            { id: "music-header", type: "block", size: { px: 40 },
              content: { mod: "music-dock", props: { header: true, terminal } } },
            { id: "music-player", type: "block", content: { terminal } },
          ] } });
        setShared(OVERLAY, { id, terminal, space: context?.space, tab: context?.tab });
      } catch (error) {
        notify({ title: "Lounge music", body: String(error.message || error), level: "error" });
      } finally { this.opening = false; cx.notify(); }
    });
  }

  close() {
    if (this.header) {
      if (shared(OVERLAY)?.id === props().overlay) setShared(OVERLAY, null);
    } else this.hide();
    // Hiding, layout switches and app quit leave the core terminal and playback alone.
  }

  render(cx) {
    const t = theme();
    if (this.header) {
      return h_flex().size_full().px(14).gap(12).items_center().bg(t.chrome).text_color(t.foreground)
        .child(div().flex_1().text_size(13).child("Lounge · GrooveNet"))
        .child(div().text_size(11).text_color(t.muted).child("Cmd-Shift-M hides · player keys work inside"))
        .child(div().id("music-hide").px(10).py(5).rounded(5).cursor_pointer().hover(s => s.bg(t.hover))
          .on_click(() => this.hide()).child("Hide"));
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
