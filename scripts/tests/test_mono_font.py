import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
FONT = runpy.run_path(str(ROOT / 'zsh/.local/bin/mono-font'))
CATALOG = json.loads((ROOT / 'fonts/monospace.json').read_text())


class MonoFontTests(unittest.TestCase):
    def test_local_herdr_settings_preserve_machine_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            path = home / '.config/herdr-app/settings.json'
            path.parent.mkdir(parents=True)
            path.write_text('{"zoom": 1.1, "theme": "catppuccin", "sounds": {"enabled": false}}')
            rendered = FONT['render'](ROOT, CATALOG['fonts']['commit-mono'], home)
            data = json.loads(rendered[path])
            self.assertEqual(data, dict(zoom=1.1, theme='catppuccin', sounds={'enabled': False},
                                        font='CommitMono', ui_font='CommitMono'))
            path.write_text(rendered[path])
            self.assertEqual(FONT['render'](ROOT, CATALOG['fonts']['commit-mono'], home)[path], path.read_text())

    def test_every_font_round_trips_without_changing_unrelated_settings(self):
        original = FONT['render'](ROOT, CATALOG['fonts'][CATALOG['selected']])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in original:
                target = root / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            for font in CATALOG['fonts'].values():
                rendered = FONT['render'](root, font)
                for path, content in rendered.items():
                    path.write_text(content)
                self.assertEqual(FONT['render'](root, font), rendered)
                bar = (root / 'sketchybar/.config/sketchybar/sketchybarrc').read_text()
                self.assertIn('0xProto Nerd Font Mono:Regular:15.0', bar)
                self.assertIn(font['family'] + ':' + font['bar_style'] + ':12.0', bar)
                for path, content in FONT['render'](root, CATALOG['fonts'][CATALOG['selected']]).items():
                    self.assertEqual(content, original[ROOT / path.relative_to(root)])

    def test_missing_setting_aborts_render_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = FONT['render'](ROOT, CATALOG['fonts'][CATALOG['selected']])
            for path, content in original.items():
                target = root / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            path = root / 'zed/.config/zed/settings.json'
            path.write_text(path.read_text().replace('"buffer_font_family"', '"removed_font_family"'))
            before = {p: p.read_text() for p in root.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(ValueError, 'expected 3 font settings, found 2'):
                FONT['render'](root, CATALOG['fonts']['space-mono'])
            self.assertEqual(before, {p: p.read_text() for p in before})


if __name__ == '__main__':
    unittest.main()
