import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

source = Path(__file__).resolve().parents[1] / 'setup-herdr-app-visor'
loader = importlib.machinery.SourceFileLoader('setup_visor', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
setup = importlib.util.module_from_spec(spec)
loader.exec_module(setup)


class GuiVisorInstallTests(unittest.TestCase):
    def test_preview_then_merge_backup_and_idempotent_reinstall(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            keys = root / 'keys.json'
            original = {'global': {'cmd-t': 'tab.new'}, 'terminal': {'cmd-c': 'terminal.copy'}}
            keys.write_text(json.dumps(original))
            (root / 'settings.json').write_text('{"zoom": 1.2}')
            setup.install(root)
            self.assertEqual(json.loads(keys.read_text()), original)
            self.assertFalse((root / 'mods').exists())
            setup.install(root, apply=True)
            installed = json.loads(keys.read_text())
            self.assertEqual(installed['global']['cmd-i'], setup.ACTION)
            del installed['global']['cmd-i']
            self.assertEqual(installed, original)
            self.assertEqual((root / 'settings.json').read_text(), '{"zoom": 1.2}')
            backup = next(root.glob('visor-backup-*'))
            self.assertEqual(json.loads((backup / 'keys.json').read_text()), original)
            setup.install(root, apply=True)
            self.assertEqual(len(list(root.glob('visor-backup-*'))), 1)

    def test_conflicting_specific_binding_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = '{"global": {}, "terminal": {"cmd-i": "terminal"}}'
            (root / 'keys.json').write_text(original)
            with self.assertRaisesRegex(ValueError, 'terminal'):
                setup.install(root, apply=True)
            self.assertEqual((root / 'keys.json').read_text(), original)
            self.assertFalse((root / 'mods').exists())
