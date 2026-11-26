import json
from pathlib import Path
import runpy
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]
SETUP = runpy.run_path(str(ROOT / 'scripts/setup-agent-statuslines'))
CLAUDE = runpy.run_path(str(ROOT / 'claude/.claude/statusline-command.py'))


class AgentStatuslineTests(unittest.TestCase):
    def test_codex_replaces_multiline_items_preserving_theme_and_other_settings(self):
        original = ('model = "test"\n[tui]\nstatus_line = [\n"model",\n"git-branch"\n]\n'
                    'theme = "dotfiles-desktop"\n[tui.other]\nenabled = true\n')
        result = SETUP['codex_settings'](original)
        expected = tomllib.loads(original)
        expected['tui'].update(status_line=SETUP['ITEMS'], status_line_use_colors=True)
        self.assertEqual(tomllib.loads(result), expected)
        self.assertEqual(result, SETUP['codex_settings'](result))

    def test_codex_adds_tui_and_retains_preferences(self):
        result = SETUP['codex_settings']('model = "test"\n')
        self.assertEqual(tomllib.loads(result)['model'], 'test')
        self.assertEqual(tomllib.loads(result)['tui']['status_line'], SETUP['ITEMS'])

    def test_claude_matches_layout_and_does_not_show_branch_or_duplicate_model(self):
        data = {'model': {'display_name': 'Opus'}, 'effort': {'level': 'high'},
                'workspace': {'current_dir': '/tmp/project'},
                'context_window': {'remaining_percentage': 75, 'used_percentage': 25},
                'rate_limits': {'five_hour': {'used_percentage': 20}}}
        self.assertEqual(CLAUDE['render'](data, False),
                         'Opus (high) | /tmp/project | ctx 75% left | 25% used | 5h 80% left')

    def test_missing_data_and_control_characters(self):
        self.assertEqual(CLAUDE['render']({}, False), '')
        data = {'model': {'display_name': 'Opus\n\x1b]0;bad\x07'},
                'context_window': {'used_percentage': 0, 'remaining_percentage': None},
                'rate_limits': None}
        result = CLAUDE['render'](data, False)
        self.assertNotIn('\x1b', result)
        self.assertNotIn('\n', result)
        self.assertIn('ctx 100% left | 0% used', result)
        self.assertNotIn('5h', result)
        self.assertIsNone(CLAUDE['percentage'](float('nan')))

    def test_local_claude_hooks_and_preferences_survive_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config = home / '.claude/settings.json'
            config.parent.mkdir()
            original = {'hooks': {'Stop': [{'hooks': []}]}, 'model': 'opus',
                        'statusLine': {'type': 'command', 'command': 'old', 'padding': 2}}
            config.write_text(json.dumps(original))
            result = SETUP['render'](home, home / '.codex')
            updated = json.loads(result[config])
            self.assertEqual(updated['hooks'], original['hooks'])
            self.assertEqual(updated['model'], original['model'])
            self.assertEqual(updated['statusLine']['padding'], 2)
            self.assertEqual(json.loads(config.read_text()), original)


if __name__ == '__main__':
    unittest.main()
