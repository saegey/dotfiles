import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


source = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-linear-titles'
loader = importlib.machinery.SourceFileLoader('herdr_linear_titles', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
titles = importlib.util.module_from_spec(spec)
loader.exec_module(titles)


class LinearTitleTests(unittest.TestCase):
    def test_recognizes_branch_and_worktree_ids(self):
        for name in ['adam/SKY-6712', 'adam-sky-6712', 'sky-6712-description', 'feature/ENG2-42']:
            self.assertEqual(titles.ticket_id(name), 'ENG2-42' if 'ENG2' in name else 'SKY-6712')
        for name in ['main', 'skysafe-cloud', 'feature/no-ticket']:
            self.assertIsNone(titles.ticket_id(name))

    def test_branch_takes_priority_over_directory(self):
        workspace = {'label': 'SKY-333', 'worktree': {'checkout_path': '/tmp/adam-sky-222'}}
        response = subprocess.CompletedProcess([], 0, stdout='adam/SKY-111\n')
        with patch.object(titles.subprocess, 'run', return_value=response):
            self.assertEqual(titles.workspace_ticket(workspace), 'SKY-111')

    def test_detached_branch_falls_back_to_directory(self):
        workspace = {'label': 'Custom label', 'worktree': {'checkout_path': '/tmp/adam-sky-222'}}
        response = subprocess.CompletedProcess([], 1, stdout='')
        with patch.object(titles.subprocess, 'run', return_value=response):
            self.assertEqual(titles.workspace_ticket(workspace), 'SKY-222')

    def test_review_badge_tracks_current_branch(self):
        workspace = {'workspace_id': 'w1', 'worktree': {'checkout_path': '/tmp/repo'}}
        listed = subprocess.CompletedProcess([], 0, stdout=json.dumps({
            'result': {'workspaces': [workspace]}}))
        with patch.dict(titles.os.environ, {'HERDR_ENV': '1'}):
            for branch, expected in [('other/feature', 'review=[R]'),
                                     ('adam/feature', 'review'),
                                     ('main', 'review'),
                                     ('adam-other/feature', 'review=[R]'),
                                     ('', 'review')]:
                with self.subTest(branch=branch):
                    with patch.object(titles, 'workspace_branch', return_value=branch), \
                         patch.object(titles.subprocess, 'run', return_value=listed) as run:
                        titles.refresh()
                    args = run.call_args.args[0]
                    index = args.index(expected)
                    self.assertEqual(args[index - 1],
                                     '--token' if expected == 'review=[R]' else '--clear-token')

    def test_missing_or_unreadable_worktree_has_no_branch(self):
        self.assertEqual(titles.workspace_branch({}), '')
        workspace = {'worktree': {'checkout_path': '/tmp/repo'}}
        with patch.object(titles.subprocess, 'run', side_effect=FileNotFoundError()):
            self.assertEqual(titles.workspace_branch(workspace), '')

    def test_sanitizes_controls_and_preserves_unicode(self):
        self.assertEqual(titles.clean_title('Fix\n  reader\tprobe\x00 — café'), 'Fix reader probe — café')
        self.assertIsNone(titles.clean_title(None))

    def test_caches_titles_and_force_bypasses_cache(self):
        response = subprocess.CompletedProcess([], 0, stdout=json.dumps({
            'identifier': 'SKY-123', 'title': 'Readable title'}))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(titles.subprocess, 'run', return_value=response) as run:
                args = ('SKY-123', '/tmp/repo', '/tmp/repo', Path(directory))
                self.assertEqual(titles.lookup_title(*args), 'Readable title')
                self.assertEqual(titles.lookup_title(*args), 'Readable title')
                self.assertEqual(run.call_count, 1)
                self.assertEqual(titles.lookup_title(*args, force=True), 'Readable title')
                self.assertEqual(run.call_count, 2)
                self.assertEqual(run.call_args.kwargs['env']['LINEAR_IGNORE_ENV_FILE'], '1')
            cached = next(Path(directory).glob('*.json'))
            self.assertEqual(cached.stat().st_mode & 0o777, 0o600)

    def test_offline_lookup_keeps_last_known_title(self):
        response = subprocess.CompletedProcess([], 0, stdout=json.dumps({
            'identifier': 'SKY-123', 'title': 'Cached title'}))
        with tempfile.TemporaryDirectory() as directory:
            args = ('SKY-123', '/tmp/repo', '/tmp/repo', Path(directory))
            with patch.object(titles.subprocess, 'run', return_value=response):
                titles.lookup_title(*args)
            with patch.object(titles.subprocess, 'run', side_effect=FileNotFoundError()):
                self.assertEqual(titles.lookup_title(*args, force=True), 'Cached title')

    def test_rejects_mismatched_ticket_and_scopes_by_repo(self):
        response = subprocess.CompletedProcess([], 0, stdout=json.dumps({
            'identifier': 'SKY-999', 'title': 'Wrong issue'}))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(titles.subprocess, 'run', return_value=response) as run:
                for scope in ['/tmp/repo-a', '/tmp/repo-b']:
                    self.assertIsNone(titles.lookup_title('SKY-123', scope, scope, Path(directory)))
                self.assertEqual(run.call_count, 2)
                self.assertEqual(len(list(Path(directory).glob('*.json'))), 2)

    def test_requires_herdr_context(self):
        with patch.dict(titles.os.environ, {'HERDR_ENV': ''}):
            with self.assertRaises(RuntimeError):
                titles.refresh()


if __name__ == '__main__':
    unittest.main()
