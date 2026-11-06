import importlib.machinery
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

path = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-music-view'
loader = importlib.machinery.SourceFileLoader('music_view', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
view = importlib.util.module_from_spec(spec)
loader.exec_module(view)


class MusicViewTests(unittest.TestCase):
    def test_status_cleanup_falls_back_to_child_when_group_signal_is_denied(self):
        process = subprocess.Popen(
            [os.sys.executable, '-c', 'import time; time.sleep(60)'],
            stdout=subprocess.PIPE, start_new_session=True)
        try:
            with patch.object(view.os, 'killpg', side_effect=PermissionError):
                view.stop_status(process)
            self.assertIsNotNone(process.returncode)
            self.assertTrue(process.stdout.closed)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate()

    def test_status_cleanup_handles_signal_races_and_denied_child_signals(self):
        for error in (ProcessLookupError, PermissionError):
            with self.subTest(error=error):
                process = Mock(pid=123, returncode=None)
                process.poll.return_value = None
                process.kill.side_effect = error
                process.communicate.side_effect = subprocess.TimeoutExpired('status', 1)
                with patch.object(view.os, 'killpg', side_effect=error):
                    view.stop_status(process)
                process.kill.assert_called_once_with()
                process.communicate.assert_called_once_with(timeout=1)
                process.stdout.close.assert_called_once_with()

    def test_status_cleanup_bounds_wait_for_inherited_pipe_after_child_exits(self):
        process = Mock(pid=123)
        process.poll.return_value = 0
        process.communicate.side_effect = subprocess.TimeoutExpired('status', 1)
        with patch.object(view.os, 'killpg') as killpg:
            view.stop_status(process)
        killpg.assert_not_called()
        process.kill.assert_not_called()
        process.stdout.close.assert_called_once_with()

    def test_terminal_is_restored_even_if_cache_cleanup_fails(self):
        dock = Mock()
        dock.status_cache.return_value.unlink.side_effect = PermissionError('cache')
        with patch.dict(os.environ, HERDR_SOCKET_PATH='/test/socket'), \
                patch.object(view, 'load_dock', return_value=dock), \
                patch.object(view.sys, 'argv', ['herdr-music-view']), \
                patch.object(view.os, 'isatty', return_value=True), \
                patch.object(view.os, 'get_terminal_size', side_effect=KeyboardInterrupt), \
                patch.object(view.os, 'write'), \
                patch.object(view.signal, 'signal'), \
                patch.object(view.tty, 'setraw'), \
                patch.object(view.termios, 'tcgetattr', return_value=['original']), \
                patch.object(view.termios, 'tcsetattr') as restore:
            with self.assertRaises(PermissionError):
                view.main()
        restore.assert_called_once_with(0, view.termios.TCSADRAIN, ['original'])

    def test_symlinked_view_finds_real_siblings_after_link_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / 'checkout with spaces'
            checkout.mkdir()
            shutil.copy2(path, checkout / path.name)
            shutil.copy2(path.with_name('herdr-music-dock'), checkout / 'herdr-music-dock')
            link = root / 'herdr-music-view'
            link.symlink_to(checkout / path.name)
            loader = importlib.machinery.SourceFileLoader('linked_music_view', str(link))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            linked = importlib.util.module_from_spec(spec)
            loader.exec_module(linked)
            link.unlink()
            self.assertEqual(linked.HELPER_DIR, checkout.resolve())
            self.assertEqual(linked.load_dock().MUSIC_LAUNCHER, checkout.resolve() / 'herdr-music')

    def test_launcher_finds_siblings_without_home_bin_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / 'checkout with spaces'
            checkout.mkdir()
            launcher = checkout / 'herdr-music'
            shutil.copy2(path.with_name('herdr-music'), launcher)
            fake_view = checkout / 'herdr-music-view'
            fake_view.write_text('#!/bin/sh\nprintf "sibling view:%s\\n" "$1"\n')
            fake_view.chmod(0o755)
            link = root / 'music link'
            link.symlink_to(Path('checkout with spaces/herdr-music'))
            result = subprocess.run([str(link), '--cached-status'],
                                    env=dict(os.environ, HOME=str(root)),
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'sibling view:--cached-status')

    def test_no_alias_file_uses_cli_with_selected_remote(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = root / 'groovenet'
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            fake.chmod(0o755)
            env = dict(os.environ, HOME=str(root), HERDR_MUSIC_REMOTE='office',
                       PATH=str(root) + os.pathsep + os.environ['PATH'])
            result = subprocess.run([str(path.with_name('herdr-music')), '--status'],
                                    env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.splitlines(),
                             ['status', '--remote', 'office', '--max-width', '42', '--bar-width', '4'])

    def test_status_cannot_wrap_or_inject_control_sequences(self):
        self.assertEqual(view.status_line('\x1b[31mTrack\x1b[0m\nArtist', 9), 'Track Ar')
        self.assertEqual(view.status_line('曲曲abc', 5), '曲曲')
        self.assertEqual(view.status_line('abc', 0), '')

    def test_parked_player_never_expands(self):
        def api(method, **kwargs):
            self.assertEqual(method, 'session.snapshot')
            return {'snapshot': {'panes': [{'pane_id': 'w1:p1', 'tokens': {
                'music_lounge': '1', 'music_hidden': '1'}}]}}
        self.assertFalse(view.expanded(api))

    def test_expanded_view_requires_music_to_be_zoomed(self):
        def api(method, **kwargs):
            if method == 'session.snapshot':
                return {'snapshot': {'panes': [{'pane_id': 'w1:p2', 'tab_id': 'w1:t1',
                                              'tokens': {'music_lounge': '1'}}]}}
            return {'layout': {'zoomed': True, 'focused_pane_id': 'w1:p2'}}
        self.assertTrue(view.expanded(api))

    def test_work_pane_zoom_does_not_expand_music(self):
        def api(method, **kwargs):
            if method == 'session.snapshot':
                return {'snapshot': {'panes': [{'pane_id': 'w1:p2', 'tab_id': 'w1:t1',
                                              'tokens': {'music_lounge': '1'}}]}}
            return {'layout': {'zoomed': True, 'focused_pane_id': 'w1:p1'}}
        self.assertFalse(view.expanded(api))


if __name__ == '__main__':
    unittest.main()
