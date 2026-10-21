import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch


source = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-worktree-visor'
loader = importlib.machinery.SourceFileLoader('worktree_visor', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
visor = importlib.util.module_from_spec(spec)
loader.exec_module(visor)


class WorktreeVisorTests(unittest.TestCase):
    def test_safe_urls(self):
        for url in ['https://example.app.localhost', 'http://localhost:1338', 'https://github.com/org/repo/pull/1']:
            self.assertEqual(visor.safe_url(url), url)
        for url in ['javascript:alert(1)', 'file:///tmp/file', 'https://user:secret@example.com',
                    'https://host:bad', 'https://host/\x1b[31m', 'https://host/a b', None]:
            self.assertIsNone(visor.safe_url(url))

    def test_reads_only_literal_app_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docker/localdev').mkdir(parents=True)
            (root / 'docker/localdev/.env').write_text(
                'TOKEN=secret\nCOMPOSE_PROJECT_NAME=localdev-example\n'
                'export SKYCLOUD_API_V1_BASE_URL="https://example.api.localhost/v1"\n'
                'WEBAPP_PORT=1338 # comment\nSHELL=$(touch /tmp/never-execute)\n')
            values = visor.read_app_env(root)
            self.assertEqual(values['SKYCLOUD_API_V1_BASE_URL'], 'https://example.api.localhost/v1')
            self.assertEqual(values['WEBAPP_PORT'], '1338')
            self.assertNotIn('TOKEN', values)
            self.assertNotIn('SHELL', values)

    def test_uses_actual_caddy_routes_and_env(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docker/localdev').mkdir(parents=True)
            (root / 'docker/localdev/.env').write_text(
                'COMPOSE_PROJECT_NAME=localdev-example\nWEBAPP_PORT=1777\n'
                'SKYCLOUD_BASE_URL=https://webapp.localdev-example.orb.local\n')
            conf = root / 'conf'
            conf.mkdir()
            (conf / 'example.caddy').write_text(
                'example.app.localhost, https://example.localhost {\n'
                'reverse_proxy https://localhost:1777\n}\nexample.api.localhost {\n}\n')
            links = visor.app_links(root, [], conf)
            urls = [item['url'] for item in links]
            self.assertEqual(urls[0], 'https://example.app.localhost')
            self.assertIn('https://example.api.localhost/v1', urls)
            self.assertIn('https://webapp.localdev-example.orb.local', urls)
            self.assertIn('https://localhost:1777', urls)
            self.assertEqual(len(urls), len(set(urls)))

    def test_no_guessed_app_links(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(visor.app_links(Path(directory), [], Path(directory)), [])

    def test_focused_pane_checkout_precedes_workspace(self):
        context = {'focused_pane_cwd': '/tmp/worktree/subdir', 'workspace_cwd': '/tmp/main'}
        with patch.object(visor, 'run', return_value='/tmp/worktree') as run:
            self.assertEqual(visor.resolve_checkout(context=context), Path('/tmp/worktree').resolve())
            self.assertEqual(run.call_args.args[1], '/tmp/worktree/subdir')

    def test_failed_explicit_path_does_not_fall_back(self):
        with patch.object(visor, 'run', side_effect=FileNotFoundError()):
            with self.assertRaises(RuntimeError):
                visor.resolve_checkout('/missing', {'workspace_cwd': '/tmp/main'})

    def test_actions_match_commit_and_latest_workflow_event(self):
        runs = [dict(workflowName='Tests', event='push', headSha='current', url='new'),
                dict(workflowName='Tests', event='push', headSha='current', url='old'),
                dict(workflowName='Tests', event='pull_request', headSha='current', url='pr'),
                dict(workflowName='Deploy', event='push', headSha='other', url='wrong')]
        self.assertEqual([run['url'] for run in visor.latest_runs(runs, 'current')], ['new', 'pr'])

    def test_mismatched_pr_is_rejected(self):
        with patch.object(visor, 'read_json', return_value={'headRefName': 'another-branch'}):
            self.assertIsNone(visor.load_pr(Path('/tmp'), 'adam/SKY-123')['pr'])

    def test_missing_pr_is_normal(self):
        error = subprocess.CalledProcessError(1, ['gh'], stderr='no pull requests found for branch')
        with patch.object(visor, 'read_json', side_effect=error):
            self.assertEqual(visor.load_pr(Path('/tmp'), 'adam/SKY-123'), {'pr': None, 'error': None})

    def test_popup_keeps_explicit_worktree_context(self):
        with patch.dict(visor.os.environ, {'HERDR_ENV': '1', 'HERDR_WORKSPACE_ID': 'w9'}):
            with patch.object(visor.subprocess, 'run') as run:
                visor.launch_popup(Path('/tmp/worktree'))
                args = run.call_args.args[0]
                self.assertIn('VISOR_CWD=/tmp/worktree', args)
                self.assertNotIn('--workspace', args)
                self.assertNotIn('--target-pane', args)

    def test_only_http_links_are_opened_without_a_shell(self):
        with patch.object(visor.subprocess, 'Popen') as open_process:
            visor.open_url('javascript:alert(1)')
            open_process.assert_not_called()
            visor.open_url('https://example.app.localhost')
            self.assertEqual(open_process.call_args.args[0][-1], 'https://example.app.localhost')
            self.assertNotIn('shell', open_process.call_args.kwargs)

    def test_cancels_owned_collector_when_closed(self):
        fetch = visor.Fetch.__new__(visor.Fetch)
        fetch.output = io.StringIO()
        fetch.process = MagicMock(pid=123456)
        fetch.process.poll.return_value = None
        with patch.object(visor.os, 'killpg') as kill:
            fetch.close()
            kill.assert_called_once_with(123456, visor.signal.SIGTERM)
        self.assertTrue(fetch.output.closed)

    def test_fetch_initialization_uses_owned_process_group(self):
        with patch.object(visor.subprocess, 'Popen') as start:
            start.return_value.poll.return_value = 0
            fetch = visor.Fetch(Path('/tmp/worktree'))
            self.assertTrue(start.call_args.kwargs['start_new_session'])
            self.assertIn('--json', start.call_args.args[0])
            self.assertEqual(start.call_args.args[0][-1], '/tmp/worktree')
            fetch.close()

    def test_escape_closes_loading_screen(self):
        screen = MagicMock()
        screen.getmaxyx.return_value = (24, 80)
        screen.getch.return_value = 27
        with patch.object(visor, 'Fetch') as fetch:
            fetch.return_value.done.return_value = False
            visor.display(screen, Path('/tmp/worktree'))
            fetch.return_value.close.assert_called_once()

    def test_summary_and_links_precede_long_ticket_description(self):
        data = {
            'apps': [], 'head': 'abc123',
            'linear': {'issue': {'identifier': 'SKY-1', 'title': 'Title',
                       'state': {'name': 'In Progress'}, 'description': 'Long description',
                       'url': 'https://linear.app/team/issue/SKY-1'}, 'error': None},
            'github': {'pr': None, 'error': None},
            'actions': {'runs': [], 'error': None},
            'stacks': {'projects': [], 'error': None},
        }
        rows = visor.rows_for(data, 80)
        headings = [row['text'] for row in rows if row['heading']]
        self.assertLess(headings.index('GITHUB PULL REQUEST'), headings.index('TICKET DESCRIPTION'))
        self.assertTrue(any(row['url'] == 'https://linear.app/team/issue/SKY-1' for row in rows))


if __name__ == '__main__':
    unittest.main()
