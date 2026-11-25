import { View, div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { theme, props, shared, setShared, closeOverlay } from "herdr";

const OVERLAY = "dotfiles.music.overlay";

export default class MusicHeader extends View {
  hide() {
    const overlay = shared(OVERLAY);
    if (!overlay) return;
    setShared(OVERLAY, null);
    closeOverlay(overlay.id);
  }

  close() {
    if (shared(OVERLAY)?.id === props().overlay) setShared(OVERLAY, null);
  }

  render() {
    const t = theme();
    return h_flex().size_full().px(14).gap(12).items_center().bg(t.chrome).text_color(t.foreground)
      .child(div().flex_1().text_size(13).child("Lounge · GrooveNet"))
      .child(div().text_size(11).text_color(t.muted).child("Cmd-Option-M hides · player keys work inside"))
      .child(div().id("music-hide").px(10).py(5).rounded(5).cursor_pointer().hover(s => s.bg(t.hover))
        .on_click(() => this.hide()).child("Hide"));
  }
}
