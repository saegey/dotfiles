# Browser monospace font

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
