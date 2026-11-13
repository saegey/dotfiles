import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-agent'
GIT_USER = ['-c', 'user.name=Test', '-c', 'user.email=test@example.com']


class HerdrAgentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / 'home'
        self.home.mkdir()
        self.main = self.root / 'main repo'
        self.main.mkdir()
        self.git('init', '-b', 'main')
        self.git(*GIT_USER, 'commit', '--allow-empty', '-m', 'Initial')
        # Checkouts land where the app's worktree mod puts them.
        self.worktrees = self.home / '.herdr/worktrees/main repo'
        self.log = self.root / 'herdr-app.log'
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        app = bin_dir / 'herdr-app'
        app.write_text('''#!/bin/bash
set -eu
printf '%s\\n' "$(jq -cn '$ARGS.positional' --args -- "$@")" >> "$TEST_LOG"
case "$1" in
  ls) [[ -z "${TEST_LS_FAIL:-}" ]] || exit 1; printf '%s\\n' "$TEST_SPACES" ;;
  do) [[ "$2" == space.new ]] && echo '{"space":"spNEW","terminal":"t9"}' || echo '{}' ;;
esac
''')
        app.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ('HERDR_AGENT', 'HERDR_MODEL', 'HERDR_ENV')}
        self.env.update(HOME=str(self.home), TEST_LOG=str(self.log),
                        PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
                        GIT_CONFIG_NOSYSTEM='1',
                        TEST_SPACES=json.dumps({'spaces': [
                            {'id': 'spOLD', 'name': 'old', 'folder': str(self.main),
                             'machine': None, 'active': True, 'tabs': []}]}))

    def git(self, *args, cwd=None):
        return subprocess.run(['git', '-C', str(cwd or self.main), *args],
                              text=True, capture_output=True, check=True)

    def run_helper(self, *args, cwd=None):
        return subprocess.run(['bash', str(HELPER), *args], cwd=cwd or self.main,
                              env=self.env, text=True, capture_output=True, timeout=20)

    def dry(self, *args, branch='feat/x'):
        result = self.run_helper(branch, '--dry-run', *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        fields = dict(re.findall(r'^(\w+): +(.*)$', result.stdout, re.M))
        fields['argv'] = json.loads(fields['argv'])
        return fields

    def tab(self, *args):
        """The setup step and the agent argv a dry run would launch."""
        argv = self.dry(*args)['argv']
        if not argv:
            return None
        self.assertEqual(argv[:2], ['/bin/bash', '-c'])
        return argv[4], argv[5:]

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def space_new(self):
        new = [c for c in self.calls() if c[:2] == ['do', 'space.new']]
        self.assertEqual(len(new), 1, self.calls())
        return json.loads(new[0][2])

    # Setup discovery and the agent command.

    def test_just_recipe_runs_before_the_agent(self):
        (self.main / 'justfile').write_text('worktree-setup *args:\n  echo hi\n')
        self.assertEqual(self.tab('--prompt', 'go'), ('just worktree-setup', ['claude', 'go']))

    def test_setup_script_is_the_fallback(self):
        script = self.main / 'scripts/worktree-setup.sh'
        script.parent.mkdir()
        script.write_text('#!/bin/sh\n')
        script.chmod(0o755)
        self.assertEqual(self.tab(), ('./scripts/worktree-setup.sh', ['claude']))

    def test_repo_without_setup_starts_only_the_agent(self):
        (self.main / 'justfile').write_text('worktree-up:\n  echo hi\n')
        self.assertEqual(self.tab(), ('', ['claude']))

    def test_explicit_setup_overrides_and_no_setup_skips(self):
        (self.main / 'justfile').write_text('worktree-setup:\n  echo hi\n')
        self.assertEqual(self.tab('--setup', 'just bootstrap'), ('just bootstrap', ['claude']))
        self.assertEqual(self.tab('--no-setup'), ('', ['claude']))

    def test_no_agent_runs_only_setup_and_nothing_is_a_plain_shell(self):
        self.assertEqual(self.tab('--setup', 'make', '--no-agent'), ('make', []))
        self.assertIsNone(self.tab('--no-agent'))

    def test_flags_win_over_preset_and_env_defaults(self):
        self.env.update(HERDR_AGENT='codex', HERDR_MODEL='env-model')
        self.assertEqual(self.tab('--no-setup'), ('', ['codex', '--model', 'env-model']))
        self.assertEqual(self.tab('--no-setup', '--preset', 'review', '--pr', '1',
                                  '--agent', 'claude', '--model', 'sonnet', '--prompt', 'mine'),
                         ('', ['claude', '--model', 'sonnet', 'mine']))

    def test_plan_preset_fills_the_ticket_and_needs_one(self):
        _, agent = self.tab('--preset', 'plan', '--ticket', 'SKY-1')
        self.assertIn('ticket SKY-1 ', agent[-1])
        result = self.run_helper('feat/x', '--dry-run', '--preset', 'plan')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('needs --ticket', result.stderr)

    def test_rejects_unsafe_model_unknown_agent_and_bad_branch(self):
        bad_model = self.run_helper('feat/x', '--dry-run', '--model', 'x;rm -rf ~')
        self.assertNotEqual(bad_model.returncode, 0)
        self.assertIn('--model may only contain', bad_model.stderr)
        bad_agent = self.run_helper('feat/x', '--dry-run', '--agent', 'vim')
        self.assertNotEqual(bad_agent.returncode, 0)
        self.assertIn('unknown agent', bad_agent.stderr)
        bad_branch = self.run_helper('feat x', '--dry-run')
        self.assertNotEqual(bad_branch.returncode, 0)
        self.assertIn('not a valid branch', bad_branch.stderr)

    def test_prompt_file_is_passed_verbatim(self):
        prompt = self.root / 'prompt.txt'
        prompt.write_text("it's $(touch pwned) `go`\nline two")
        self.assertEqual(self.tab('--no-setup', '--prompt-file', str(prompt)),
                         ('', ['claude', "it's $(touch pwned) `go`\nline two"]))

    def test_launch_script_runs_setup_then_agent_and_stops_on_failure(self):
        argv = self.dry('--setup', 'echo setup; (exit "$SETUP_STATUS")', '--prompt', "it's $(go)")['argv']
        argv[5] = 'printf'  # the "agent": print its arguments
        argv[6:] = ['[%s]', *argv[6:]]
        ok = subprocess.run(argv, env=dict(self.env, SETUP_STATUS='0'),
                            capture_output=True, text=True)
        self.assertEqual(ok.stdout, "setup\n[it's $(go)]")
        failed = subprocess.run(argv, env=dict(self.env, SETUP_STATUS='3'),
                                capture_output=True, text=True)
        self.assertEqual(failed.returncode, 3)
        self.assertEqual(failed.stdout, 'setup\n')
        self.assertIn('agent was not started', failed.stderr)

    # Worktree placement and git.

    def test_dry_run_prints_the_plan_and_changes_nothing(self):
        fields = self.dry(branch='Adam/SKY-6830')
        path = self.worktrees / 'adam-sky-6830'
        self.assertEqual(fields['worktree'], str(path))
        self.assertIn('worktree add --no-track -b Adam/SKY-6830', fields['git'])
        self.assertTrue(fields['git'].endswith(' HEAD'), fields['git'])
        self.assertFalse(path.exists())
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.git('branch', '--list', 'Adam/SKY-6830').stdout, '')

    def test_creates_from_main_checkout_when_run_in_a_linked_worktree(self):
        linked = self.root / 'linked'
        self.git('worktree', 'add', '-b', 'other', str(linked))
        self.git(*GIT_USER, 'commit', '--allow-empty', '-m', 'On other', cwd=linked)
        result = self.run_helper('feat/x', '--prompt', 'go', cwd=linked)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.worktrees / 'feat-x'
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=path).stdout,
                         self.git('rev-parse', 'main').stdout)
        args = self.space_new()
        self.assertEqual({k: args[k] for k in ('name', 'folder', 'machine', 'tab')},
                         {'name': 'feat/x', 'folder': str(path), 'machine': '', 'tab': 'claude'})
        self.assertEqual(args['argv'][4:], ['', 'claude', 'go'])
        self.assertNotIn(['do', 'space.select', '{"id":"spOLD"}'], self.calls())

    def test_base_and_remote_branches(self):
        remote = self.root / 'remote.git'
        subprocess.run(['git', 'init', '--bare', '-b', 'main', str(remote)], check=True,
                       capture_output=True)
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', 'origin', 'main', 'main:pushed')
        self.git('fetch', 'origin')
        self.git('remote', 'set-head', 'origin', 'main')
        # review: --base origin/<same branch> tracks it.
        fields = self.dry('--base', 'origin/pushed', branch='pushed')
        self.assertIn('fetch --quiet origin pushed', fields['fetch'])
        self.assertIn('worktree add --track -b pushed', fields['git'])
        # A branch only on origin is tracked without --base; others start from origin's default.
        self.assertIn('--track -b pushed', self.dry(branch='pushed')['git'])
        self.assertTrue(self.dry()['git'].endswith(' origin/main'))
        result = self.run_helper('pushed', '--base', 'origin/pushed', '--no-agent', '--no-focus')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('rev-parse', '--abbrev-ref', 'pushed@{u}').stdout.strip(),
                         'origin/pushed')
        self.assertIn(['do', 'space.select', '{"id":"spOLD"}'], self.calls())

    def test_existing_local_branch_is_checked_out_as_is(self):
        self.git('branch', 'feat/x')
        self.git(*GIT_USER, 'commit', '--allow-empty', '-m', 'Ahead on main')
        result = self.run_helper('feat/x', '--base', 'main', '--no-agent')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('already exists', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=self.worktrees / 'feat-x').stdout,
                         self.git('rev-parse', 'feat/x').stdout)

    def test_existing_worktree_is_reused_and_its_space_selected(self):
        path = self.root / 'elsewhere'
        self.git('worktree', 'add', '-b', 'feat/x', str(path))
        self.env['TEST_SPACES'] = json.dumps({'spaces': [
            {'id': 'spX', 'folder': str(path), 'machine': None, 'active': False, 'tabs': []}]})
        result = self.run_helper('feat/x', '--prompt', 'go')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [['ls'], ['do', 'space.select', '{"id":"spX"}']])
        # Without a space, one is opened on it (and nothing is created by git).
        self.env['TEST_SPACES'] = json.dumps({'spaces': []})
        result = self.run_helper('feat/x', '--no-setup')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.space_new()['folder'], str(path))
        self.assertFalse((self.worktrees / 'feat-x').exists())

    def test_existing_path_is_never_clobbered(self):
        path = self.worktrees / 'feat-x'
        path.mkdir(parents=True)
        (path / 'keep').write_text('mine')
        result = self.run_helper('feat/x')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('leaving it untouched', result.stderr)
        self.assertEqual((path / 'keep').read_text(), 'mine')
        self.assertEqual(self.git('branch', '--list', 'feat/x').stdout, '')

    def test_branch_in_main_checkout_is_refused(self):
        result = self.run_helper('main', '--dry-run')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('main checkout', result.stderr)

    def test_refuses_without_the_app(self):
        self.env['TEST_LS_FAIL'] = '1'
        result = self.run_helper('feat/x')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("can't reach the Herdr app", result.stderr)
        self.assertFalse((self.worktrees / 'feat-x').exists())


if __name__ == '__main__':
    unittest.main()
