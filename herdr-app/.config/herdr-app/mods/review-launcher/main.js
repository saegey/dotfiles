import { View, div } from "gpui-kit";
import { appHome, exec, props, closeOverlay, notify, theme } from "herdr";

export default class ReviewLauncher extends View {
  init(_initial, cx) {
    const overlay = props()?.overlay;
    // The native checker has no overlay; loading/checking never starts programs.
    if (!overlay) return;
    cx.spawn(async cx => {
      try {
        const result = await exec("bash", ["-c", 'export PATH="$HOME/.local/share/mise/shims:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"; exec "$HOME/.local/bin/herdr-gui-review" --app-home "$1"', "review", appHome()], { timeout: 45000 });
        if (result.code !== 0) throw new Error(result.stderr || result.stdout || "Could not open Review");
      } catch (error) {
        notify({ title: "Review dashboard", body: String(error.message || error).slice(0, 1000), level: "error" });
      } finally { closeOverlay(overlay); }
    });
  }

  render() {
    const t = theme();
    return div().size_full().flex().items_center().justify_center().bg(t.chrome)
      .text_size(13).text_color(t.foreground).child("Opening Review…");
  }
}
