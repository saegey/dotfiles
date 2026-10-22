import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-wt-done'


class WorktreeDoneTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.main = self.root / 'main repo'
        self.main.mkdir()
        self.git('init', '-b', 'main')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                 'commit', '--allow-empty', '-m', 'Initial')
        self.worktree = self.root / 'review worktree'
        self.git('worktree', 'add', '-b', 'review', str(self.worktree))
        self.log = self.root / 'herdr.log'
        binary = self.root / 'herdr'
        binary.write_text('''#!/bin/bash
set -eu
if [[ "$*" == "workspace list" ]]; then
  printf '%s\\n' "$TEST_WORKSPACES"
else
  printf '%s\\n' "$*" >> "$TEST_LOG"
  exit "${TEST_REMOVE_STATUS:-0}"
fi
''')
        binary.chmod(0o755)
        docker = self.root / 'docker'
        docker.write_text('''#!''' + sys.executable + '''
import json, os, pathlib, sys
args = sys.argv[1:]
log = pathlib.Path(os.environ['TEST_LOG'] + '.docker')
with log.open('a') as output:
    output.write(json.dumps(args) + '\\n')
if os.environ.get('TEST_DOCKER_FAIL') == args[0]:
    sys.exit(1)
records = json.loads(os.environ.get('TEST_DOCKER_RECORDS', '[]'))
removed = pathlib.Path(os.environ['TEST_LOG'] + '.removed')
if args[0] == 'ps':
    if not removed.exists():
        print('\\n'.join(c['Id'] for c in records))
elif args[0] == 'inspect':
    print(json.dumps(records))
elif args[0] == 'rm':
    removed.touch()
elif len(args) > 1 and args[1] == 'ls':
    print('resource-' + args[0])
''')
        docker.chmod(0o755)
        self.env = dict(os.environ, HERDR_ENV='1', HERDR_WORKSPACE_ID='w2',
                        PATH=str(self.root) + os.pathsep + os.environ['PATH'],
                        HERDR_BIN_PATH=str(binary), HERDR_ACTIVE_PANE_CWD=str(self.worktree),
                        TEST_LOG=str(self.log), TEST_WORKSPACES=json.dumps({'result': {
                            'workspaces': [{'workspace_id': 'w2', 'worktree': {
                                'checkout_path': str(self.worktree)}}]}}))

    def git(self, *args, cwd=None):
        return subprocess.run(['git', '-C', str(cwd or self.main), *args],
                              text=True, capture_output=True, check=True)

    def run_helper(self, *args):
        return subprocess.run(['bash', str(HELPER), *args], cwd=self.main,
                              env=self.env, text=True, capture_output=True, timeout=5)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ''

    def test_generic_repo_uses_native_removal(self):
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), 'worktree remove --workspace w2\n')

    def test_force_is_forwarded_to_native_removal(self):
        result = self.run_helper('-f')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), 'worktree remove --workspace w2 --force\n')

    def test_native_refusal_does_not_close_workspace(self):
        self.env['TEST_REMOVE_STATUS'] = '1'
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertNotIn('workspace close', self.calls())
        self.assertTrue(self.worktree.exists())

    def test_main_checkout_is_refused(self):
        self.env['HERDR_ACTIVE_PANE_CWD'] = str(self.main)
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('main checkout', result.stderr)
        self.assertEqual(self.calls(), '')

    def test_workspace_mismatch_is_refused(self):
        self.env['TEST_WORKSPACES'] = json.dumps({'result': {'workspaces': [
            {'workspace_id': 'w2', 'worktree': {'checkout_path': str(self.main)}}]}})
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('belongs to', result.stderr)
        self.assertEqual(self.calls(), '')

    def test_cleanup_failure_preserves_workspace(self):
        for checkout in [self.main, self.worktree]:
            with self.subTest(checkout=checkout):
                scripts = checkout / 'scripts'
                scripts.mkdir()
                cleanup = scripts / 'worktree-rm.sh'
                cleanup.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$TEST_LOG"\nexit 9\n')
                cleanup.chmod(0o755)
                result = self.run_helper('--force')
                self.assertEqual(result.returncode, 9, result.stderr)
                self.assertEqual(self.calls(), '--force\n' + str(self.worktree) + '\n')
                self.assertTrue(self.worktree.exists())

    def test_unpushed_commits_require_force(self):
        self.git('branch', '--set-upstream-to=main', 'review')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                 'commit', '--allow-empty', '-m', 'Unpushed', cwd=self.worktree)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unpushed commits', result.stderr)
        self.assertEqual(self.calls(), '')
        result = self.run_helper('--force')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unexpected_arguments_are_refused(self):
        result = self.run_helper('/some/other/worktree')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), '')

    def stack(self, directory, project='review-stack', identifier='container-1'):
        return {'Id': identifier, 'Config': {'Labels': {
            'com.docker.compose.project': project,
            'com.docker.compose.project.working_dir': str(directory)}}}

    def test_stack_and_resources_are_removed_before_worktree(self):
        self.env['TEST_DOCKER_RECORDS'] = json.dumps([self.stack(self.worktree / 'docker/localdev')])
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = [json.loads(line) for line in Path(str(self.log) + '.docker').read_text().splitlines()]
        self.assertIn(['rm', '--force', '--volumes', 'container-1'], calls)
        self.assertIn(['volume', 'rm', 'resource-volume'], calls)
        self.assertIn(['network', 'rm', 'resource-network'], calls)
        self.assertIn('worktree remove', self.calls())

    def test_stack_failure_keeps_worktree_even_with_force(self):
        self.env['TEST_DOCKER_RECORDS'] = json.dumps([self.stack(self.worktree)])
        self.env['TEST_DOCKER_FAIL'] = 'rm'
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('leaving worktree', result.stderr)
        self.assertEqual(self.calls(), '')

    def test_unavailable_docker_refuses_removal(self):
        self.env['TEST_DOCKER_FAIL'] = 'ps'
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.calls(), '')

    def test_shared_stack_is_refused(self):
        self.env['TEST_DOCKER_RECORDS'] = json.dumps([
            self.stack(self.worktree), self.stack(self.main, identifier='container-2')])
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('shared with another checkout', result.stderr)
        self.assertEqual(self.calls(), '')

    def test_other_checkout_stack_is_untouched(self):
        self.env['TEST_DOCKER_RECORDS'] = json.dumps([self.stack(self.main)])
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = Path(str(self.log) + '.docker').read_text()
        self.assertNotIn('"rm"', calls)

    def test_dirty_worktree_is_refused_before_stack_teardown(self):
        (self.worktree / 'new-file').write_text('unsaved')
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsaved work', result.stderr)
        self.assertFalse(Path(str(self.log) + '.docker').exists())


if __name__ == '__main__':
    unittest.main()
