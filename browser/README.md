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

## GitHub website colors

`desktop-theme <id>` also generates `browser/github-theme.user.css` for Stylus.
It maps the shared palette onto GitHub's Primer color variables: page and panel
backgrounds, borders, text, links, buttons, syntax highlighting, and diff colors.
Additions and deletions retain separate tinted backgrounds. Light palettes use
light appearance. This style only applies to github.com and can be installed
alongside the existing monospace style below.

In Stylus, open **Manage**, then drag `github-theme.user.css` from Finder onto
that page and click **Install style**. Refresh a GitHub tab to check the result.
For changes to follow `desktop-theme`, enable **Live reload** in the installer
and keep that installer tab open. Current Chromium versions support watching
the individually dropped file, without enabling access to every file URL.
When the installer is closed, reimport the file after switching palettes.
Stylus stores an imported copy; regenerating the file alone does not change it.
See [Stylus local-file/live reload instructions](https://github.com/openstyles/stylus/wiki/Writing-UserCSS#live-reload-on-the-fly-previewing).

Remove `github` from `themes/catalog.json` to stop generating this export;
disable the style in Stylus to restore GitHub's own colors. GitHub may add
components or change its CSS tokens, so check a repository, an issue, and a diff
after installing. This does not change your GitHub account appearance setting.
Token references: [Primer theme reference](https://primer.style/product/getting-started/react/theme-reference/).

## Gmail website colors

`desktop-theme <id>` generates `browser/gmail-theme.user.css` for Stylus.
Install it from **Stylus → Manage** by dragging the file onto that page, then
click **Install style**. As with the GitHub export, enable **Live reload** and
leave its installer tab open to follow palette changes; otherwise reimport.

The style is limited to mail.google.com. It colors Gmail's navigation, search,
inbox rows, menus, reading-pane chrome, and compose UI, preserving unread weight
and a distinct selected-row state. It supports both light and dark palettes.
Received message bodies stay on a light surface with dark default text;
sender-defined colors, links, images, and layouts remain intact. This keeps
rich newsletters and receipts readable without image inversion. Compose
formatting is inherited normally, rather than overriding every child element.

The export changes no Gmail settings or message data. Disable the style in
Stylus to restore Gmail's own appearance; remove `gmail` from
`themes/catalog.json` to stop exporting it. Gmail changes its generated class
names over time, so check an inbox, an opened message, and a compose window
after installing. Chat and other embedded Google apps are outside this style.

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
