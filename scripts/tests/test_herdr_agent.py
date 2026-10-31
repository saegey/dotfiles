import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-agent'


class HerdrAgentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.main = self.root / 'main repo'
        self.main.mkdir()
        self.git('init', '-b', 'main')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                 'commit', '--allow-empty', '-m', 'Initial')
        # Where the fake Herdr "creates" the worktree.
        self.worktree = self.root / 'new worktree'
        self.worktree.mkdir()
        self.log = self.root / 'herdr.log'
        binary = self.root / 'herdr'
        binary.write_text('''#!/bin/bash
set -eu
printf '%s\\n' "$(printf '%q ' "$@")" >> "$TEST_LOG"
if [[ "$1 $2" == "worktree create" ]]; then
  printf '%s\\n' "$TEST_CREATED"
fi
''')
        binary.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items() if k not in ('HERDR_AGENT', 'HERDR_MODEL')}
        self.env.update(HERDR_ENV='1', HERDR_BIN_PATH=str(binary), TEST_LOG=str(self.log),
                        TMPDIR=str(self.root),
                        TEST_CREATED=json.dumps({'result': {
                            'worktree': {'path': str(self.worktree)},
                            'root_pane': {'pane_id': 'w9:p1'}}}))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.main), *args],
                              text=True, capture_output=True, check=True)

    def run_helper(self, *args, cwd=None):
        return subprocess.run(['bash', str(HELPER), *args], cwd=cwd or self.main,
                              env=self.env, text=True, capture_output=True, timeout=10)

    def dry_command(self, *args):
        result = self.run_helper('feat/x', '--dry-run', *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return re.search(r'^command:  (.*)$', result.stdout, re.M).group(1)

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def test_just_recipe_runs_before_the_agent(self):
        (self.main / 'justfile').write_text('worktree-setup *args:\n  echo hi\n')
        self.assertEqual(self.dry_command('--prompt', 'go'),
                         "just worktree-setup && claude \"$(cat '<prompt file>')\"")

    def test_setup_script_is_the_fallback(self):
        script = self.main / 'scripts/worktree-setup.sh'
        script.parent.mkdir()
        script.write_text('#!/bin/sh\n')
        script.chmod(0o755)
        self.assertEqual(self.dry_command(), './scripts/worktree-setup.sh && claude')

    def test_repo_without_setup_starts_only_the_agent(self):
        (self.main / 'justfile').write_text('worktree-up:\n  echo hi\n')
        self.assertEqual(self.dry_command(), 'claude')

    def test_explicit_setup_overrides_and_no_setup_skips(self):
        (self.main / 'justfile').write_text('worktree-setup:\n  echo hi\n')
        self.assertEqual(self.dry_command('--setup', 'just bootstrap'), 'just bootstrap && claude')
        self.assertEqual(self.dry_command('--no-setup'), 'claude')

    def test_no_agent_runs_only_setup(self):
        self.assertEqual(self.dry_command('--setup', 'make', '--no-agent'), 'make')

    def test_review_preset_uses_opus_and_fills_the_pr(self):
        result = self.run_helper('feat/x', '--preset', 'review', '--pr', '12', '--no-setup',
                                 '--no-focus')
        self.assertEqual(result.returncode, 0, result.stderr)
        run = next(c for c in self.calls() if c.startswith('pane run'))
        prompt_file = re.search(r"cat\\ \\'([^\\]+)\\'", run).group(1)
        self.assertIn('claude\\ --model\\ opus', run)
        self.assertEqual(Path(prompt_file).read_text(), '/pr-review 12\n')

    def test_flags_win_over_preset_and_env_defaults(self):
        self.env.update(HERDR_AGENT='codex', HERDR_MODEL='env-model')
        self.assertEqual(self.dry_command('--no-setup'), 'codex --model env-model')
        self.assertEqual(self.dry_command('--no-setup', '--preset', 'review', '--pr', '1',
                                          '--agent', 'claude', '--model', 'sonnet',
                                          '--prompt', 'mine'),
                         "claude --model sonnet \"$(cat '<prompt file>')\"")

    def test_plan_preset_needs_a_ticket(self):
        result = self.run_helper('feat/x', '--dry-run', '--preset', 'plan')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('needs --ticket', result.stderr)

    def test_rejects_unsafe_model_and_unknown_agent(self):
        bad_model = self.run_helper('feat/x', '--dry-run', '--model', 'x;rm -rf ~')
        self.assertNotEqual(bad_model.returncode, 0)
        self.assertIn('--model may only contain', bad_model.stderr)
        bad_agent = self.run_helper('feat/x', '--dry-run', '--agent', 'vim')
        self.assertNotEqual(bad_agent.returncode, 0)
        self.assertIn('unknown agent', bad_agent.stderr)

    def test_creates_from_main_checkout_when_run_in_a_linked_worktree(self):
        linked = self.root / 'linked'
        self.git('worktree', 'add', '-b', 'other', str(linked))
        (self.worktree / 'justfile').write_text('worktree-setup:\n  echo hi\n')
        result = self.run_helper('feat/x', '--base', 'origin/main', '--prompt', "it's go",
                                 cwd=linked)
        self.assertEqual(result.returncode, 0, result.stderr)
        create, run = self.calls()
        self.assertTrue(create.startswith('worktree create --cwd ' +
                                          str(self.main).replace(' ', '\\ ') + ' '), create)
        self.assertIn('--base origin/main', create)
        self.assertIn('--focus', create)
        self.assertTrue(run.startswith('pane run w9:p1 just\\ worktree-setup\\ \\&\\&\\ claude'), run)
        prompt_file = re.search(r"cat\\ \\'([^\\]+)\\'", run).group(1)
        self.assertEqual(Path(prompt_file).read_text(), "it's go\n")

    def test_refuses_outside_herdr(self):
        self.env['HERDR_ENV'] = '0'
        result = self.run_helper('feat/x')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inside a Herdr terminal', result.stderr)
        self.assertEqual(self.calls(), [])


if __name__ == '__main__':
    unittest.main()
