import { View, div } from "gpui-kit";
import { focused, spaces, props, run, closeOverlay, notify } from "herdr";
export default class TasksLauncher extends View {
  init() {
    const overlay = props()?.overlay;
    if (!overlay) return;
    const f = focused();
    const space = spaces().find(s => s.id === f?.space);
    const folder = f?.cwd || space?.folder;
    if (folder) run("terminal.open", {folder, place: "right", name: "Repo tasks",
      argv: ["bash", "-lc", 'export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"; exec "$HOME/.local/bin/herdr-repo-tasks"']});
    else notify({title: "Repo tasks", body: "Focus a repository terminal first.", level: "error"});
    closeOverlay(overlay);
  }
  render() { return div(); }
}
