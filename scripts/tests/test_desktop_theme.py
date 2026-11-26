import json
import plistlib
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
PRESETS = tuple(path.stem for path in sorted((ROOT / 'themes/palettes').glob('*.json')))


def copy_configs(root):
    for rel in THEME['CONFIGS'].values():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
    shutil.copytree(ROOT / 'themes', root / 'themes')


class DesktopThemeTests(unittest.TestCase):
    def test_base16_mapping_overrides_inheritance_and_validation(self):
        for key in ('everforest', 'gruvbox-material', 'kanagawa'):
            raw = json.loads((ROOT / 'themes/palettes' / (key + '.json')).read_text())
            colors = THEME['palette'](ROOT, key)['colors']
            self.assertEqual(set(colors), THEME['COLORS'])
            self.assertEqual(colors['background'], raw['base16']['base00'])
            self.assertEqual(colors['foreground'], raw['base16']['base05'])
            self.assertEqual(colors['red'], raw['base16']['base08'])
            self.assertEqual(colors['selection'], raw['base16']['base02'])
            self.assertEqual(colors['accent'], raw['colors'].get('accent', raw['base16']['base0D']))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'themes', root / 'themes')
            path = root / 'themes/palettes/custom.json'
            path.write_text(json.dumps({'extends': 'everforest', 'colors': {'accent': '#123456'}}))
            colors = THEME['palette'](root, 'custom')['colors']
            self.assertEqual(colors['accent'], '#123456')
            self.assertEqual(colors['background'], '#272e33')
            data = json.loads((root / 'themes/palettes/everforest.json').read_text())
            del data['base16']['base0F']
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'exactly base00 through base0F'):
                THEME['palette'](root, 'custom')
            data['base16']['base0F'] = 'bad'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, '#rrggbb'):
                THEME['palette'](root, 'custom')

    def test_codex_preserves_local_settings_and_uses_shared_colors(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            custom_home = home / 'custom-codex'
            custom_home.mkdir()
            config = custom_home / 'config.toml'
            original = ('model = "my-model"\n# local preferences\n[tui]\n'
                        'theme = "nord" # keep this comment\nstatus_line = ["model"]\n'
                        '[tui.other]\nenabled = true\n')
            config.write_text(original)
            for key in PRESETS:
                theme = THEME['palette'](ROOT, key)
                result = THEME['render'](ROOT, theme, ['codex'], home, custom_home)
                data = tomllib.loads(result[config])
                expected = tomllib.loads(original)
                expected['tui']['theme'] = 'dotfiles-desktop'
                self.assertEqual(data, expected)
                self.assertIn('# keep this comment', result[config])
                self.assertEqual(THEME['codex_config'](result[config]), result[config])
                asset = custom_home / 'themes/dotfiles-desktop.tmTheme'
                parsed = plistlib.loads(result[asset].encode())
                self.assertEqual(parsed['settings'][0]['settings']['background'], theme['colors']['background'])
                scopes = {v['scope']: v['settings'] for v in parsed['settings'][1:]}
                self.assertEqual(scopes['keyword']['foreground'], theme['colors']['blue'])
                self.assertEqual(scopes['string']['foreground'], theme['colors']['green'])
            self.assertEqual(config.read_text(), original)  # render/dry run never writes

    def test_codex_adds_missing_tui_and_skips_uninstalled_cli(self):
        for original in ('model = "test"\n', '[tui]\nstatus_line = []\n'):
            result = THEME['codex_config'](original)
            self.assertEqual(tomllib.loads(result)['tui']['theme'], 'dotfiles-desktop')
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = THEME['render'](ROOT, THEME['palette'](ROOT, 'nord'), ['codex'], home)
            self.assertFalse(any(p.is_relative_to(home) for p in result))

    def test_chrome_export_tracks_palette_without_scripts_or_permissions(self):
        for key in PRESETS:
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
            for key in (*PRESETS, 'mocha'):
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
