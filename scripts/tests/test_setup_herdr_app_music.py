import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

source = Path(__file__).resolve().parents[1] / 'setup-herdr-app-music'
loader = importlib.machinery.SourceFileLoader('setup_music', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
setup = importlib.util.module_from_spec(spec)
loader.exec_module(setup)


class GuiMusicInstallTests(unittest.TestCase):
    def layout(self):
        return {'id': 'root', 'type': 'column', 'theme': 'catppuccin', 'children': [
            {'id': 'tabs', 'type': 'block', 'size': {'px': 42}, 'content': {'mod': 'tabs'}},
            {'id': 'work', 'type': 'block', 'content': {'tab': 'active'}}]}

    def test_layout_preserves_existing_tree_and_can_be_reapplied(self):
        original = self.layout()
        updated = setup.music_layout(original)
        self.assertEqual(original, self.layout())
        self.assertEqual(updated['theme'], original['theme'])
        self.assertEqual(updated['children'][1], original['children'][1])
        bar = updated['children'][0]
        self.assertEqual(bar['size'], {'px': 42})
        self.assertEqual(bar['children'][0]['id'], 'tabs')
        self.assertEqual(bar['children'][1]['content']['mod'], 'music-dock')
        self.assertEqual(setup.music_layout(updated), updated)

    def test_key_merge_preserves_visor_and_rejects_specific_conflicts(self):
        original = {'global': {'cmd-i': 'mod.open:worktree-visor'}, 'terminal': {'cmd-c': 'terminal.copy'}}
        merged = setup.merged_keys(original)
        self.assertEqual(merged['global']['cmd-i'], original['global']['cmd-i'])
        self.assertEqual(merged['terminal'], original['terminal'])
        self.assertNotIn('cmd-shift-m', original['global'])
        original['terminal']['cmd-alt-m'] = 'terminal'
        with self.assertRaisesRegex(ValueError, 'terminal'):
            setup.merged_keys(original)

    def test_install_clones_layout_and_backs_up_keys_without_touching_shipped_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'layouts').mkdir()
            original = json.dumps(self.layout())
            (root / 'layouts/main.json').write_text(original)
            (root / 'keys.json').write_text('{"global":{"cmd-i":"mod.open:worktree-visor"}}')
            def command(app_home, *args):
                if args == ('status',):
                    return {'layout': 'main'}
                self.assertEqual(args, ('do', 'layout.clone', '--name', 'main', '--as', 'main-music'))
                (root / 'layouts/main-music.json').write_text(original)
                return {'ok': True}
            with patch.object(setup, 'command', side_effect=command):
                setup.install(root)
                self.assertFalse((root / 'mods').exists())
                setup.install(root, apply=True)
            self.assertEqual((root / 'layouts/main.json').read_text(), original)
            self.assertEqual(json.loads((root / 'layouts/main-music.json').read_text())['children'][0]['id'], 'music-tabbar')
            self.assertEqual(json.loads((root / 'keys.json').read_text())['global']['cmd-i'], 'mod.open:worktree-visor')
            self.assertEqual(len(list(root.glob('music-backup-*'))), 1)

    def test_incompatible_layout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no tabs'):
            setup.music_layout({'id': 'root', 'type': 'block', 'content': {'mod': 'win98'}})
