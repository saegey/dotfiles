# Browser appearance

## Chrome theme

Every `desktop-theme <id>` also exports the selected palette as a Chrome theme
in `browser/themes/chrome/`. Custom palettes use the same export. This changes
browser chrome (frame, toolbar, tabs, address field and new-tab colors), not
the content of websites.
The export includes solid active/inactive frame PNGs, explicit background-tab
colors, and neutral frame tints to improve coverage of Chrome's vertical tabs.
Chrome's native sidebar coverage varies by version; reapply the export to
check the result in the installed version.

To try it in your chosen Chrome profile:

1. Open `chrome://extensions` and enable **Developer mode**.
2. Click **Load unpacked** and select this checkout's `browser/themes/chrome`
   directory, which contains `manifest.json`.
3. Accept any theme confirmation Chrome shows.

The export is a theme-only extension: no scripts or permissions. It is an
imported copy; Chrome does not automatically follow edits to its manifest.
After changing the desktop palette, reapply the folder through **Load unpacked**
(or reload it if your Chrome version exposes that control). It applies per
profile. You can return to Chrome's default from **Settings → Appearance →
Reset to default**. Remove `chrome` from `themes/catalog.json` to stop exports.

This is an export with manual application, not a live Chrome integration.
Vivaldi supports editable themes, ZIP imports and schedules, but its documented
interface does not provide an external command to apply arbitrary palette
changes live. Firefox offers a WebExtension `theme.update` API if a future
browser integration needs fully automatic color updates.

References: [Chrome themes](https://developer.chrome.com/docs/extensions/develop/ui/themes),
[Vivaldi themes](https://help.vivaldi.com/desktop/appearance-customization/browser-themes/),
[Firefox theme API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/theme/update).

## Browser monospace font

`mono-font.user.css` applies Maple Mono to code on github.com and linear.app,
including GitHub's source/diff views and comment editor. Normal interface text
keeps the website's font. It uses the locally installed Maple Mono family and
does not download fonts. It applies to browser tabs, not Linear's desktop app.

Install [Stylus](https://github.com/openstyles/stylus), open its **Manage** page,
and drag `mono-font.user.css` from Finder onto that page. Click **Install style**
if prompted, then refresh GitHub and Linear. This import method does not require
enabling access to all file URLs. See the [Stylus installation instructions](https://github.com/openstyles/stylus/wiki/Writing-UserCSS#installing-local-files).

This style is separate from the `mono-font` command for desktop apps. To change
its font, edit `--dotfiles-mono` in the file and reimport it, or edit the installed
style in Stylus. Imports are copies; future dotfiles edits do not automatically
update the installed style. Website-specific selectors may need upkeep as sites
change; verify a GitHub diff and a Linear issue containing code after installing.
