import json
from pathlib import Path
import runpy
import re
import shutil
import tempfile
import unittest
import tomllib
from unittest.mock import patch
import subprocess


ROOT = Path(__file__).resolve().parents[2]
THEME = runpy.run_path(str(ROOT / 'zsh/.local/bin/desktop-theme'))
TARGETS = json.loads((ROOT / 'themes/catalog.json').read_text())['targets']


def copy_configs(root):
    for rel in THEME['CONFIGS'].values():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
    shutil.copytree(ROOT / 'themes', root / 'themes')


class DesktopThemeTests(unittest.TestCase):
    def test_chrome_export_tracks_palette_without_scripts_or_permissions(self):
        for key in ('mocha', 'frappe', 'nord', 'solarized-dark'):
            theme = THEME['palette'](ROOT, key)
            content = THEME['assets']('chrome', theme['colors'])['browser/themes/chrome/manifest.json']
            manifest = json.loads(content)
            self.assertNotIn('permissions', manifest)
            self.assertNotIn('background', manifest)
            self.assertEqual(manifest['manifest_version'], 3)
            exported = THEME['assets']('chrome', theme['colors'])
            for image in manifest['theme']['images'].values():
                png = exported['browser/themes/chrome/' + image]
                self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertIn('background_tab_inactive', manifest['theme']['colors'])
            self.assertEqual(manifest['theme']['tints']['frame'], [-1, -1, -1])
            rgb = manifest['theme']['colors']['toolbar']
            self.assertEqual('#' + ''.join(f'{v:02x}' for v in rgb), theme['colors']['background'])
            custom = {**theme['colors'], 'accent': '#123456'}
            data = json.loads(THEME['assets']('chrome', custom)['browser/themes/chrome/manifest.json'])
            self.assertEqual(data['theme']['colors']['ntp_link'], [18, 52, 86])

    def test_macos_ghostty_override_is_updated_without_changing_font(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            path = home / 'Library/Application Support/com.mitchellh.ghostty/config.ghostty'
            path.parent.mkdir(parents=True)
            path.write_text('theme = dark:Catppuccin Mocha,light:Catppuccin Mocha\nfont-family = JetBrains Mono\n')
            local = home / '.config/ghostty/config'
            local.parent.mkdir(parents=True)
            local.write_text((ROOT / THEME['CONFIGS']['ghostty']).read_text())
            result = THEME['render'](ROOT, THEME['palette'](ROOT, 'nord'), TARGETS, home)
            self.assertEqual(result[path], 'theme = dotfiles-desktop\nfont-family = JetBrains Mono\n')

    def test_live_apply_uses_herdr_theme_command_and_exact_ghostty_process(self):
        with patch('shutil.which', return_value='/bin/tool'), patch('subprocess.run') as run, patch('os.kill') as kill:
            run.side_effect = [subprocess.CompletedProcess([], 0, '{"ok":true}', ''),
                               subprocess.CompletedProcess([], 0, '123\n', '')]
            THEME['reload_apps'](['herdr-app', 'ghostty'])
            self.assertEqual(run.call_args_list[0].args[0], ['herdr-app', 'do', 'app.theme', '--name', 'dotfiles-desktop'])
            self.assertEqual(run.call_args_list[1].args[0], ['pgrep', '-x', 'ghostty'])
            kill.assert_called_once_with(123, THEME['signal'].SIGUSR2)

    def test_switches_are_idempotent_and_preserve_fonts_and_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_configs(root)
            reference = None
            for key in ('mocha', 'frappe', 'nord', 'solarized-dark', 'mocha'):
                theme = THEME['palette'](root, key)
                rendered = THEME['render'](root, theme, TARGETS)
                THEME['write_files'](rendered)
                self.assertEqual(rendered, THEME['render'](root, theme, TARGETS))
                if key == 'mocha':
                    if reference is None:
                        reference = rendered
                    else:
                        self.assertEqual(reference, rendered)
                for app in ('herdr', 'hunk', 'dinky', 'starship'):
                    tomllib.loads((root / THEME['CONFIGS'][app]).read_text())
                zed = (root / THEME['CONFIGS']['zed']).read_text()
                self.assertIn('"dark": "Catppuccin Mocha"', zed)  # icon theme
                font_line = re.search(r'^  "buffer_font_family":.*$', (ROOT / THEME['CONFIGS']['zed']).read_text(), re.MULTILINE)[0]
                self.assertIn(font_line, zed)
                ghostty = (root / THEME['CONFIGS']['ghostty']).read_text()
                font_line = re.search(r'^font-family =.*$', (ROOT / THEME['CONFIGS']['ghostty']).read_text(), re.MULTILINE)[0]
                self.assertIn(font_line, ghostty)
                self.assertIn('keybind = cmd+t=unbind', ghostty)
                herdr = (root / THEME['CONFIGS']['herdr']).read_text()
                self.assertIn('new_tab = "cmd+t"', herdr)
                self.assertEqual(herdr.count('[theme.custom]'), 1)
                self.assertNotIn('ghzinga', TARGETS)

    def test_local_settings_are_merged_and_generated_assets_are_installed(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            path = home / '.config/herdr-app/settings.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'theme': 'graphite', 'zoom': 1.2, 'font': 'My Font', 'sounds': {'enabled': False}}))
            theme = THEME['palette'](ROOT, 'nord')
            rendered = THEME['render'](ROOT, theme, TARGETS, home)
            data = json.loads(rendered[path])
            self.assertEqual(data['theme'], 'dotfiles-desktop')
            self.assertEqual(data['zoom'], 1.2)
            self.assertEqual(data['font'], 'My Font')
            self.assertEqual(data['sounds'], {'enabled': False})
            generated = home / '.config/herdr-app/themes/dotfiles-desktop.json'
            self.assertEqual(json.loads(rendered[generated])['background'], '#2e3440')
            self.assertNotIn(home / '.config/ghostty/themes/dotfiles-desktop', rendered)

    def test_custom_palette_inherits_and_rejects_invalid_colors_and_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'themes', root / 'themes')
            path = root / 'themes/palettes/custom.json'
            data = {'extends': 'mocha', 'colors': {'accent': '#123456'}}
            path.write_text(json.dumps(data))
            self.assertEqual(THEME['palette'](root, 'custom')['colors']['accent'], '#123456')
            self.assertEqual(THEME['palette'](root, 'custom')['colors']['background'], '#1e1e2e')
            data['colors']['accent'] = 'oops'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, '#rrggbb'):
                THEME['palette'](root, 'custom')
            path.write_text('{"extends": "custom"}')
            with self.assertRaisesRegex(ValueError, 'cycle'):
                THEME['palette'](root, 'custom')
            with self.assertRaisesRegex(ValueError, 'Theme IDs'):
                THEME['palette'](root, '../../file')

    def test_bad_target_aborts_without_writing_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_configs(root)
            path = root / THEME['CONFIGS']['dinky']
            path.write_text(path.read_text().replace('active-color =', 'removed-color ='))
            before = {p: p.read_text() for p in root.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(ValueError, 'dinky: Expected'):
                THEME['render'](root, THEME['palette'](root, 'nord'), TARGETS)
            self.assertEqual(before, {p: p.read_text() for p in before})

    def test_external_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            external = home / 'outside.json'
            external.write_text('{}')
            path = home / '.config/herdr-app/settings.json'
            path.parent.mkdir(parents=True)
            path.symlink_to(external)
            with self.assertRaisesRegex(ValueError, 'outside this checkout'):
                THEME['render'](ROOT, THEME['palette'](ROOT, 'mocha'), TARGETS, home)


if __name__ == '__main__':
    unittest.main()
