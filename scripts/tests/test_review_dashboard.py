import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch


def load(name):
    source = Path(__file__).resolve().parents[2] / 'herdr/.local/bin' / name
    loader = importlib.machinery.SourceFileLoader(name, str(source))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


opener = load('herdr-pr-open')
review = load('herdr-review')


class ReviewDashboardTests(unittest.TestCase):
    def setUp(self):
        self.pr = dict(number=12, title='SKY-12 Improve something', headRefName='adam/SKY-12',
                       headRefOid='a' * 40, baseRefName='main', isCrossRepository=False)
        self.source = {'repo_root': '/tmp/repo'}

    def test_remote_identity_handles_personal_and_work_ssh_aliases(self):
        for remote in ['git@github.com:skysafe/cloud.git', 'git@github-skysafe:skysafe/cloud.git',
                       'https://github.com/skysafe/cloud.git', 'ssh://git@github.com/skysafe/cloud.git']:
            self.assertEqual(opener.remote_repo(remote), 'skysafe/cloud')
        self.assertIsNone(opener.remote_repo('https://example.com/skysafe/cloud.git'))

    def test_empty_successful_pane_run_response_is_accepted(self):
        with patch.object(review.subprocess, 'run', return_value=types.SimpleNamespace(stdout='')):
            self.assertEqual(review.herdr('pane', 'run', 'w1:p1', 'gh dash'), {})
        with patch.object(opener, 'call', return_value=''):
            self.assertEqual(opener.herdr('workspace', 'focus', 'w1'), {})

    def test_existing_branch_checkout_is_reused(self):
        worktree = dict(branch='adam/SKY-12', is_linked_worktree=True,
                        path='/tmp/existing checkout', open_workspace_id='w9')
        plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source, [worktree])
        self.assertEqual(plan['operation'], 'reuse')
        with patch.object(opener, 'call', return_value=self.pr['headRefOid']) as call, \
             patch.object(opener, 'herdr') as herdr:
            opener.execute_plan(plan, self.pr)
        self.assertEqual(call.call_args.args[0], ['git', 'rev-parse', 'HEAD'])
        self.assertEqual(call.call_count, 1, 'Existing checkout must not be fetched or reset')
        herdr.assert_called_once_with('workspace', 'focus', 'w9')

    def test_closed_workspace_reopens_existing_checkout_without_focus(self):
        worktree = dict(branch='adam/SKY-12', is_linked_worktree=True, path='/tmp/existing')
        plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source, [worktree])
        with patch.object(opener, 'call', return_value=self.pr['headRefOid']), \
             patch.object(opener, 'herdr') as herdr:
            opener.execute_plan(plan, self.pr, focus=False)
        self.assertEqual(herdr.call_args.args[:2], ('worktree', 'open'))
        self.assertIn('--no-focus', herdr.call_args.args)

    def test_fork_does_not_reuse_unrelated_same_named_branch(self):
        self.pr['isCrossRepository'] = True
        worktree = dict(branch='adam/SKY-12', is_linked_worktree=True, path='/tmp/unrelated')
        plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source, [worktree])
        self.assertEqual(plan['operation'], 'create')
        self.assertEqual(plan['branch'], 'review/pr-12')

    def test_main_checkout_is_never_reused_as_review_worktree(self):
        self.pr['headRefName'] = 'main'
        plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source,
                                [dict(branch='main', is_linked_worktree=False, path='/tmp/main')])
        self.assertEqual(plan['operation'], 'create')
        self.assertEqual(plan['branch'], 'review/pr-12')

    def test_pr_branch_in_main_directory_gets_separate_review_branch(self):
        plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source,
                                [dict(branch='adam/SKY-12', is_linked_worktree=False, path='/tmp/main')])
        self.assertEqual(plan['operation'], 'create')
        self.assertEqual(plan['branch'], 'review/pr-12')

    def test_new_worktree_fetches_pr_ref_without_resetting_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source, [], home=directory)
            with patch.object(opener, 'call', side_effect=['', self.pr['headRefOid'], '', self.pr['headRefOid']]) as call, \
                 patch.object(opener.subprocess, 'run', return_value=types.SimpleNamespace(returncode=1)), \
                 patch.object(opener, 'herdr'):
                opener.execute_plan(plan, self.pr, focus=False)
            calls = [item.args[0] for item in call.call_args_list]
            self.assertIn('+refs/pull/12/head:refs/herdr/pr/12', calls[0])
            self.assertEqual(calls[2][:5], ['git', 'worktree', 'add', '-b', 'adam/SKY-12'])
            self.assertFalse(any('reset' in args or 'checkout' in args or 'pull' in args for args in calls))

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = dict(operation='create', repo_root=directory, path=directory)
            with patch.object(opener, 'call') as call:
                with self.assertRaisesRegex(RuntimeError, 'already exists'):
                    opener.execute_plan(plan, self.pr)
                call.assert_not_called()

    def test_pr_update_during_fetch_does_not_create_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = opener.plan_open('skysafe/cloud', 12, self.pr, self.source, [], home=directory)
            with patch.object(opener, 'call', side_effect=['', 'b' * 40]) as call:
                with self.assertRaisesRegex(RuntimeError, 'PR changed'):
                    opener.execute_plan(plan, self.pr)
            self.assertEqual(call.call_count, 2)
            self.assertFalse(Path(plan['path']).exists())

    def test_dashboard_reuses_existing_review_workspace(self):
        state = {'workspaces': [{'label': 'Review', 'workspace_id': 'w8'}]}
        with patch.dict(os.environ, HERDR_ENV='1'), patch('sys.argv', ['herdr-review']), \
             patch.object(review, 'herdr', return_value=state) as herdr:
            self.assertEqual(review.main(), 0)
        self.assertEqual([call.args[:2] for call in herdr.call_args_list],
                         [('workspace', 'list'), ('workspace', 'report-metadata'), ('workspace', 'focus')])

    def test_dashboard_marker_survives_workspace_rename(self):
        state = {'workspaces': [{'label': 'Dashboard', 'workspace_id': 'w8',
                                'tokens': {'review_dashboard': '1'}}]}
        with patch.dict(os.environ, HERDR_ENV='1'), patch('sys.argv', ['herdr-review', '--no-focus']), \
             patch.object(review, 'herdr', return_value=state) as herdr:
            self.assertEqual(review.main(), 0)
        self.assertFalse(any(call.args[:2] == ('workspace', 'create') for call in herdr.call_args_list))

    def test_review_starts_opus_in_new_tab_and_prompts_selected_pr(self):
        plan = dict(repo='skysafe/cloud', pr=12, path='/tmp/review')
        def response(*args):
            if args[:2] == ('agent', 'get'):
                raise subprocess.CalledProcessError(1, ['herdr'], stderr='{"error":{"code":"agent_not_found"}}')
            if args[:2] == ('workspace', 'list'):
                return {'workspaces': [{'workspace_id': 'w7', 'worktree': {'checkout_path': '/tmp/review'}}]}
            if args[:2] == ('tab', 'create'):
                return {'root_pane': {'pane_id': 'w7:p2'}}
            return {}
        with patch.object(opener, 'herdr', side_effect=response) as herdr, \
             patch.object(opener.shutil, 'which', return_value='/bin/claude'):
            opener.start_review(plan)
        start = next(c.args for c in herdr.call_args_list if c.args[:2] == ('agent', 'start'))
        self.assertEqual(start[3:], ('--kind', 'claude', '--pane', 'w7:p2', '--', '--model', 'opus'))
        self.assertEqual(herdr.call_args.args, ('agent', 'prompt', start[2], '/pr-review 12'))

    def test_busy_or_blocked_review_is_focused_without_interruption(self):
        plan = dict(repo='skysafe/cloud', pr=12, path='/tmp/review')
        for status in ['working', 'blocked', 'unknown']:
            with self.subTest(status=status):
                agent = dict(agent='claude', cwd='/tmp/review', agent_status=status)
                with patch.object(opener, 'herdr', return_value={'agent': agent}) as herdr:
                    opener.start_review(plan)
                self.assertEqual([c.args[:2] for c in herdr.call_args_list], [('agent', 'get'), ('agent', 'focus')])

    def test_idle_review_is_reused_without_new_tab(self):
        plan = dict(repo='skysafe/cloud', pr=12, path='/tmp/review')
        agent = dict(agent='claude', cwd='/tmp/review', agent_status='idle')
        with patch.object(opener, 'herdr', return_value={'agent': agent}) as herdr:
            opener.start_review(plan, focus=False)
        self.assertEqual([c.args[:2] for c in herdr.call_args_list], [('agent', 'get'), ('agent', 'prompt')])
        self.assertEqual(herdr.call_args.args[-1], '/pr-review 12')

    def test_review_in_another_checkout_is_not_prompted(self):
        plan = dict(repo='skysafe/cloud', pr=12, path='/tmp/review')
        agent = dict(agent='claude', cwd='/tmp/another', agent_status='idle')
        with patch.object(opener, 'herdr', return_value={'agent': agent}) as herdr:
            with self.assertRaisesRegex(RuntimeError, 'another checkout'):
                opener.start_review(plan)
        self.assertEqual(herdr.call_count, 1)


if __name__ == '__main__':
    unittest.main()
