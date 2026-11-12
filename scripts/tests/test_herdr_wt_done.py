import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
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
        # herdr-app: `ls` answers from TEST_SPACES; everything else is logged.
        app = self.root / 'herdr-app'
        app.write_text('''#!/bin/bash
set -eu
if [[ "$1" == ls ]]; then
  printf '%s\\n' "$TEST_SPACES"
else
  printf 'app %s\\n' "$*" >> "$TEST_LOG"
fi
''')
        app.chmod(0o755)
        # hc: records the detached worker it was asked to start.
        hc = self.root / 'hc'
        hc.write_text('''#!/bin/bash
printf 'hc %s\\n' "$*" >> "$TEST_LOG"
exit "${TEST_HC_STATUS:-0}"
''')
        hc.chmod(0o755)
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
        self.env = {k: v for k, v in os.environ.items() if k not in ('HERDR_ENV', 'HERDR_WORKSPACE_ID')}
        self.env.update(HC_TERMINAL_ID='t7', PATH=str(self.root) + os.pathsep + os.environ['PATH'],
                        HERDR_ACTIVE_PANE_CWD=str(self.worktree), TEST_LOG=str(self.log))
        self.spaces(self.worktree)

    def spaces(self, folder, terminal='t7'):
        self.env['TEST_SPACES'] = json.dumps({'spaces': [
            {'id': 'spMAIN', 'folder': str(self.main), 'machine': None, 'tabs': [
                {'id': 'tb1', 'terminals': [{'terminal': 't1'}]}]},
            {'id': 'sp2', 'folder': str(folder), 'machine': None, 'tabs': [
                {'id': 'tb2', 'terminals': [{'terminal': terminal}]}]}]})

    def git(self, *args, cwd=None):
        return subprocess.run(['git', '-C', str(cwd or self.main), *args],
                              text=True, capture_output=True, check=True)

    def run_helper(self, *args):
        return subprocess.run(['bash', str(HELPER), *args], cwd=self.main,
                              env=self.env, text=True, capture_output=True, timeout=5)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ''

    CLOSE = ('hc run --bg --rm --no-notify --outlive-parent --cwd {main} -- '
             'herdr-app do space.close {{"id":"sp2","confirmed":true}}\n')

    def closed(self):
        return self.CLOSE.format(main=self.main)

    def test_generic_repo_uses_git_removal_then_closes_the_space(self):
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.calls(), self.closed())

    def test_force_removes_a_dirty_worktree(self):
        (self.worktree / 'new-file').write_text('unsaved')
        result = self.run_helper('-f')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.calls(), self.closed())

    def test_git_refusal_does_not_close_the_space(self):
        self.git('worktree', 'lock', str(self.worktree))
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.calls(), '')
        self.assertTrue(self.worktree.exists())

    def test_space_is_found_by_folder_outside_its_terminals(self):
        self.env.pop('HC_TERMINAL_ID')
        self.spaces(self.worktree, terminal='t8')
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        # Without hc, the close runs detached under nohup.
        for _ in range(50):
            if self.calls():
                break
            time.sleep(0.05)
        self.assertEqual(self.calls(), 'app do space.close {"id":"sp2","confirmed":true}\n')

    def test_falls_back_to_nohup_when_hc_fails(self):
        self.env['TEST_HC_STATUS'] = '1'
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        for _ in range(50):
            if 'app do' in self.calls():
                break
            time.sleep(0.05)
        self.assertIn('app do space.close {"id":"sp2","confirmed":true}\n', self.calls())

    def test_missing_space_is_refused(self):
        self.env.pop('HC_TERMINAL_ID')
        self.spaces(self.root, terminal='t8')
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Could not find the Herdr space', result.stderr)
        self.assertTrue(self.worktree.exists())

    def test_refuses_without_the_app(self):
        self.env['PATH'] = os.pathsep.join(p for p in self.env['PATH'].split(os.pathsep)
                                           if p != str(self.root) and not Path(p, 'herdr-app').exists())
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Not inside Herdr', result.stderr)
        self.assertTrue(self.worktree.exists())

    def test_main_checkout_is_refused(self):
        self.env['HERDR_ACTIVE_PANE_CWD'] = str(self.main)
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('main checkout', result.stderr)
        self.assertEqual(self.calls(), '')

    def test_space_mismatch_is_refused(self):
        self.spaces(self.main)
        result = self.run_helper('--force')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('belongs to', result.stderr)
        self.assertEqual(self.calls(), '')
        self.assertTrue(self.worktree.exists())

    def test_cleanup_failure_preserves_space(self):
        for checkout in [self.main, self.worktree]:
            with self.subTest(checkout=checkout):
                scripts = checkout / 'scripts'
                scripts.mkdir()
                cleanup = scripts / 'worktree-rm.sh'
                cleanup.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$TEST_LOG.cleanup"\nexit 9\n')
                cleanup.chmod(0o755)
                result = self.run_helper('--force')
                self.assertEqual(result.returncode, 9, result.stderr)
                self.assertEqual(Path(str(self.log) + '.cleanup').read_text(),
                                 '--force\n' + str(self.worktree) + '\n')
                self.assertEqual(self.calls(), '')
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
        self.assertFalse(self.worktree.exists())
        self.assertIn('space.close', self.calls())

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
