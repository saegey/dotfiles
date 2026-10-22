import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


source = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/dev-stack-status'
loader = importlib.machinery.SourceFileLoader('dev_stack_status', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
monitor = importlib.util.module_from_spec(spec)
loader.exec_module(monitor)


def container(project='localdev-a', directory='/tmp/repo-a/docker/localdev',
              state='running', status='Up 5 minutes', oneoff='False'):
    return dict(project=project, directory=directory, state=state, status=status, oneoff=oneoff)


def workspace(path='/tmp/repo-a', repo='skysafe-cloud'):
    return {'worktree': {'checkout_path': path, 'repo_name': repo}}


class StackStatusTests(unittest.TestCase):
    def test_counts_projects_not_containers(self):
        state = monitor.summarize([container(), container(),
                                   container('localdev-b', '/tmp/repo-b/docker/localdev')])
        self.assertEqual(state['running_stacks'], 2)
        self.assertEqual(state['projects'][0]['running'], 2)

    def test_stopped_and_partial_stacks(self):
        state = monitor.summarize([container(), container(state='exited')])
        self.assertEqual(monitor.workspace_token(state, workspace()), '[1]')
        stopped = monitor.summarize([container(state='exited')])
        self.assertEqual(stopped['running_stacks'], 0)
        self.assertEqual(monitor.workspace_token(stopped, workspace()), '[0]')

    def test_health_states(self):
        for health in ['unhealthy', 'health: starting']:
            state = monitor.summarize([container(status='Up 1 minute (' + health + ')')])
            self.assertEqual(monitor.workspace_token(state, workspace()), '[1]')

    def test_ignores_oneoff_jobs_and_unrelated_stacks(self):
        state = monitor.summarize([container(oneoff='True'), container(project='production'),
                                   container(directory='/tmp/other-stack')])
        self.assertEqual(state['running_stacks'], 0)
        self.assertEqual(state['projects'], [])

    def test_worktree_paths_match_exactly(self):
        state = monitor.summarize([container()])
        self.assertEqual(monitor.workspace_token(state, workspace()), '[1]')
        self.assertEqual(monitor.workspace_token(state, workspace('/tmp/repo-ab')), '[0]')
        self.assertIsNone(monitor.workspace_token(state, workspace('/tmp/unrelated', 'other')))
        self.assertIsNone(monitor.workspace_token(state, {}))

    def test_docker_failure_is_unknown_not_zero(self):
        with patch.object(monitor.subprocess, 'run', side_effect=FileNotFoundError()):
            state = monitor.snapshot()
        self.assertIsNone(state['running_stacks'])
        self.assertEqual(monitor.workspace_token(state, workspace()), '[?]')

    def test_invalid_docker_output_is_unknown(self):
        response = subprocess.CompletedProcess([], 0, stdout='not json')
        with patch.object(monitor.subprocess, 'run', return_value=response):
            self.assertIsNone(monitor.snapshot()['running_stacks'])

    def test_herdr_requires_caller_context(self):
        with patch.dict(monitor.os.environ, {'HERDR_ENV': ''}):
            with self.assertRaises(RuntimeError):
                monitor.report_herdr(monitor.summarize([]))


if __name__ == '__main__':
    unittest.main()
