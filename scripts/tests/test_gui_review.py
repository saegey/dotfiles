import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch


def load(name, source):
    loader = importlib.machinery.SourceFileLoader(name, str(source))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
gui = load('gui_review', ROOT / 'herdr/.local/bin/herdr-gui-review')
setup = load('setup_review', ROOT / 'scripts/setup-herdr-app-review')


class GuiReviewTests(unittest.TestCase):
    def setUp(self):
        self.pr = dict(number=12, title='SKY-12 Example', headRefName='author/SKY-12',
                       headRefOid='a' * 40, baseRefName='main', isCrossRepository=False)

    def test_dirty_reused_checkout_is_only_read(self):
        plan = dict(operation='reuse', repo_root='/repo', path='/worktree', pr=12)
        with patch.object(gui, 'call', return_value='b' * 40) as call:
            gui.ensure_checkout(plan, self.pr)
        call.assert_called_once_with(['git', 'rev-parse', 'HEAD'], Path('/worktree'))

    def test_fetch_head_race_creates_no_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = dict(operation='create', repo_root=directory, path=directory + '/new', branch='author/SKY-12', pr=12)
            with patch.object(gui, 'call', side_effect=['', 'b' * 40]) as call:
                with self.assertRaisesRegex(RuntimeError, 'PR changed'):
                    gui.ensure_checkout(plan, self.pr)
            self.assertEqual(call.call_count, 2)
            self.assertFalse(Path(plan['path']).exists())

    def test_create_preserves_existing_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = dict(operation='create', repo_root=directory, path=directory + '/new', branch='author/SKY-12', pr=12)
            with patch.object(gui, 'call', side_effect=['', 'a' * 40, '', 'b' * 40]) as call, \
                 patch.object(gui.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0)):
                gui.ensure_checkout(plan, self.pr)
            calls = [c.args[0] for c in call.call_args_list]
            self.assertEqual(calls[2], ['git', 'worktree', 'add', plan['path'], 'author/SKY-12'])
            self.assertFalse(any('reset' in c or 'checkout' in c or 'pull' in c for c in calls))

    def test_existing_destination_is_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(gui, 'call') as call, self.assertRaisesRegex(RuntimeError, 'Destination exists'):
                gui.ensure_checkout(dict(operation='create', repo_root=directory, path=directory), self.pr)
            call.assert_not_called()

    def test_renamed_dashboard_reuses_live_terminal_without_launch(self):
        with patch.object(gui, 'live_with_label', return_value='t7'), \
             patch.object(gui, 'core', return_value={'foreground': {'name': 'gh', 'pid': 2}, 'pid': 1}), \
             patch.object(gui, 'show_terminal') as show, patch.object(gui, 'app_do') as app:
            gui.open_dashboard(Path('/config'))
        show.assert_called_once_with('t7')
        app.assert_not_called()

    def test_completed_or_recovered_program_is_distinguished_from_startup(self):
        self.assertTrue(gui.root_shell({'pid': 1, 'foreground': {'pid': 1, 'name': 'zsh', 'argv': ['/bin/zsh', '-li']}}))
        self.assertFalse(gui.root_shell({'pid': 1, 'foreground': {'pid': 1, 'name': 'zsh', 'argv': ['/bin/zsh', '-lic', 'launch helper']}}))
        self.assertFalse(gui.root_shell({'pid': 1, 'foreground': {'pid': 2, 'name': 'gh', 'argv': ['gh', 'dash']}}))

    def test_worktree_parser_preserves_spaces_and_branch_names(self):
        raw = 'worktree /repo with spaces\0HEAD aaa\0branch refs/heads/main\0\0worktree /child\0HEAD bbb\0branch refs/heads/author/SKY-12\0locked reason\0\0'
        with patch.object(gui.subprocess, 'run', return_value=types.SimpleNamespace(stdout=raw)):
            records = gui.worktrees('/repo with spaces')
        self.assertFalse(records[0]['is_linked_worktree'])
        self.assertEqual(records[0]['path'], '/repo with spaces')
        self.assertTrue(records[1]['is_linked_worktree'])
        self.assertEqual(records[1]['branch'], 'author/SKY-12')

    def test_agent_reuse_never_launches_or_sends_another_prompt(self):
        plan = dict(repo='skysafe/cloud', pr=12, path='/worktree')
        for status in ('working', 'blocked', 'idle', 'done', None):
            with self.subTest(status=status), patch.object(gui, 'live_with_label', return_value='t9'), \
                 patch.object(gui, 'core', return_value={'cwd': '/worktree', 'status': status}) as core, \
                 patch.object(gui, 'show_terminal') as show, patch.object(gui, 'app_do') as app:
                self.assertEqual(gui.start_review(Path('/config'), plan, 'space'), 't9')
                core.assert_called_once_with('get', 't9')
                show.assert_called_once_with('t9')
                app.assert_not_called()

    def test_agent_in_different_checkout_is_untouched(self):
        with patch.object(gui, 'live_with_label', return_value='t9'), \
             patch.object(gui, 'core', return_value={'cwd': '/other'}), \
             patch.object(gui, 'show_terminal') as show, self.assertRaisesRegex(RuntimeError, 'another checkout'):
            gui.start_review(Path('/config'), dict(repo='skysafe/cloud', pr=12, path='/worktree'), 'space')
        show.assert_not_called()

    def test_initial_agent_task_is_single_argument_and_checks_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(gui.os.environ, HC_TERMINAL_ID='t9'), \
                 patch.object(gui.Path, 'cwd', return_value=Path(directory)), \
                 patch.object(gui, 'core') as core, patch.object(gui.os, 'execvp') as execute:
                gui.run_agent(Path('/config'), 'skysafe/cloud', 12, directory)
            execute.assert_called_once_with('claude', ['claude', '--model', 'opus', '/pr-review 12'])
            self.assertEqual(core.call_args.args[:2], ('label', 't9'))

    def test_local_space_reused_and_marker_saved_without_starting_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = dict(path=directory + '/worktree', repo='skysafe/cloud', pr=12)
            spaces = [{'id': 'remote', 'machine': 'vps', 'folder': plan['path']},
                      {'id': 'local', 'machine': None, 'folder': plan['path']}]
            with patch.object(gui, 'ensure_checkout'), patch.object(gui, 'app', return_value={'spaces': spaces}), \
                 patch.object(gui, 'app_do') as app, patch.object(gui.subprocess, 'run', return_value=types.SimpleNamespace(stdout='author/SKY-12\n')), \
                 patch.object(gui, 'start_review') as start:
                gui.open_pr(Path(directory), plan, self.pr)
            app.assert_called_once_with('space.select', id='local')
            start.assert_not_called()
            state = gui.load_state(Path(directory))
            key = str(Path(plan['path']).resolve())
            self.assertEqual(state['checkouts'][key]['pr'], 12)
            self.assertEqual(state['checkouts'][key]['branch'], 'author/SKY-12')

    def test_wrong_login_does_not_switch_accounts(self):
        with patch.object(gui, 'call', return_value='personal') as call, self.assertRaisesRegex(RuntimeError, 'adam-skysafe'):
            gui.require_work_login()
        call.assert_called_once_with(['gh', 'api', 'user', '--jq', '.login'], timeout=20)

    def test_conflicting_shortcuts_rejected_and_other_keys_preserved(self):
        keys = {'global': {'cmd-i': 'mod.open:worktree-visor'}, 'terminal': {}}
        result = setup.merged_keys(keys)
        self.assertEqual(result['global']['cmd-shift-r'], 'mod.open:review-launcher')
        self.assertEqual(result['global']['cmd-i'], keys['global']['cmd-i'])
        self.assertNotIn('cmd-shift-r', keys['global'])
        keys['terminal']['cmd-shift-r'] = 'terminal'
        with self.assertRaises(ValueError):
            setup.merged_keys(keys)


if __name__ == '__main__':
    unittest.main()
