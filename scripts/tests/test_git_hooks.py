"""Exercise post-pull reminders in real, temporary Git repositories."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[2]


class GitHookTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='dotfiles-hooks-')
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git('init', '-b', 'main')
        # Override inherited global configuration for reproducible hook behavior.
        self.git('config', '--local', 'core.hooksPath', '.git/hooks')
        for name in ('.githooks/post-merge', '.githooks/post-rewrite',
                     'scripts/check-herdr-update', 'scripts/setup-git-hooks'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, target)
        (self.root / 'herdr').mkdir()
        (self.root / 'herdr/config').write_text('initial\n')
        (self.root / 'other').write_text('initial\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Initial')
        self.git('config', '--local', '--unset', 'core.hooksPath')

    def run_command(self, *args, check=True):
        return subprocess.run(args, cwd=self.root, text=True,
                              capture_output=True, check=check)

    def git(self, *args):
        return self.run_command('git', '-c', 'commit.gpgsign=false',
                                '-c', 'user.name=Hook Test',
                                '-c', 'user.email=hook@example.invalid', *args)

    def install(self, check=True):
        return self.run_command('bash', 'scripts/setup-git-hooks', '--apply', check=check)

    def change(self, path, content):
        (self.root / path).write_text(content)
        self.git('add', path)
        self.git('commit', '-m', 'Change ' + path)

    def test_fast_forward_reminds_for_herdr_changes(self):
        self.install()
        self.git('checkout', '-b', 'incoming')
        self.change('herdr/config', 'updated\n')
        self.git('checkout', 'main')
        result = self.git('merge', '--ff-only', 'incoming')
        self.assertIn('./scripts/update-herdr', result.stderr)

    def test_unrelated_merge_is_quiet(self):
        self.install()
        self.git('checkout', '-b', 'incoming')
        self.change('other', 'unrelated\n')
        self.git('checkout', 'main')
        result = self.git('merge', '--ff-only', 'incoming')
        self.assertNotIn('./scripts/update-herdr', result.stderr)

    def test_rebase_reminds_for_incoming_herdr_changes(self):
        self.install()
        self.git('checkout', '-b', 'local')
        self.change('other', 'local work\n')
        self.git('checkout', 'main')
        self.change('herdr/config', 'incoming\n')
        self.git('checkout', 'local')
        result = self.git('rebase', 'main')
        self.assertIn('./scripts/update-herdr', result.stderr)

    def test_setup_is_repeatable(self):
        self.install()
        self.install()
        self.assertEqual(self.git('config', '--local', '--get', 'core.hooksPath').stdout.strip(),
                         '.githooks')

    def test_custom_hooks_path_is_preserved(self):
        self.git('config', '--local', 'core.hooksPath', 'custom-hooks')
        result = self.install(check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn('refusing', result.stderr)
        self.assertEqual(self.git('config', '--local', '--get', 'core.hooksPath').stdout.strip(),
                         'custom-hooks')

    def test_existing_pull_hook_is_preserved(self):
        path = self.root / '.git/hooks/post-merge'
        path.write_text('#!/bin/sh\nexit 0\n')
        result = self.install(check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn('refusing', result.stderr)
        self.assertEqual(path.read_text(), '#!/bin/sh\nexit 0\n')


if __name__ == '__main__':
    unittest.main()
