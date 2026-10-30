import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch


path = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-music-dock'
loader = importlib.machinery.SourceFileLoader('music_dock', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
dock = importlib.util.module_from_spec(spec)
loader.exec_module(dock)


class MusicDockTests(unittest.TestCase):
    def setUp(self):
        mode = patch.object(dock, 'STATUS_BAR', False)
        mode.start()
        self.addCleanup(mode.stop)
        refresh = patch.object(dock, 'refresh_work_pane')
        self.refresh = refresh.start()
        self.addCleanup(refresh.stop)

    def test_move_response_is_unwrapped(self):
        with patch.dict(os.environ, {'HERDR_SOCKET_PATH': '/tmp/example.sock'}):
            with patch.object(dock.socket, 'socket') as socket:
                connection = socket.return_value.__enter__.return_value
                connection.makefile.return_value = io.BytesIO(
                    b'{"result":{"type":"pane_move","move_result":{"changed":true}}}\n')
                self.assertEqual(dock.api('pane.move'), {'changed': True})

    def snapshot(self, music=True, same_tab=True):
        panes = [{'pane_id': 'w2:p1', 'tab_id': 'w2:t1'}]
        if music:
            panes.append({'pane_id': 'w2:p2' if same_tab else 'w1:p2',
                          'workspace_id': 'w2' if same_tab else 'w1',
                          'tab_id': 'w2:t1' if same_tab else 'w1:t1',
                          'tokens': {'music_lounge': '1', 'music_return': 'w2:p1'}})
        return {'snapshot': {'focused_tab_id': 'w2:t1', 'focused_pane_id': 'w2:p1',
                             'panes': panes}}

    def test_hidden_player_does_not_follow(self):
        snapshot = self.snapshot()
        snapshot['snapshot']['panes'][-1]['tokens']['music_hidden'] = '1'
        with patch.object(dock, 'api', return_value=snapshot) as api:
            dock.dock(follow=True)
        self.assertEqual(api.call_count, 1)

    def test_hide_parks_live_player_without_closing_it(self):
        calls = []
        def api(method, **params):
            calls.append((method, params))
            if method == 'session.snapshot':
                return self.snapshot()
            if method == 'layout.export':
                return {'layout': {'zoomed': False}}
            if method == 'pane.move':
                return {'changed': True}
            return {}
        with patch.object(dock, 'api', side_effect=api):
            dock.dock(visibility=True)
        move = calls[-1]
        self.assertEqual(move[0], 'pane.move')
        self.assertEqual(move[1]['destination']['type'], 'new_tab')
        self.assertFalse(move[1]['focus'])
        self.assertEqual(calls[-2][1]['tokens']['music_hidden'], '1')
        self.assertNotIn('pane.close', [method for method, _ in calls])
        self.refresh.assert_called_once_with('w2:p1', 'w2:t1')

    def test_follow_never_starts_player(self):
        with patch.object(dock, 'api', return_value=self.snapshot(music=False)) as api:
            dock.dock(follow=True)
        self.assertEqual(api.call_count, 1)

    def test_status_bar_focus_event_keeps_open_player_visible(self):
        with patch.object(dock, 'STATUS_BAR', True):
            with patch.object(dock, 'api', return_value=self.snapshot()) as api:
                dock.dock(follow=True)
        # pane.zoom can emit a redundant tab.focused event in the same tab.
        # That event must not immediately park the visor we just opened.
        self.assertEqual(api.call_count, 1)

    def test_status_bar_follow_does_not_open_hidden_player(self):
        snapshot = self.snapshot(same_tab=False)
        snapshot['snapshot']['panes'][-1]['tokens']['music_hidden'] = '1'
        with patch.object(dock, 'STATUS_BAR', True):
            with patch.object(dock, 'api', return_value=snapshot) as api:
                dock.dock(follow=True)
        self.assertEqual(api.call_count, 1)

    def test_follow_in_same_tab_does_not_restart_player(self):
        with patch.object(dock, 'api', side_effect=[self.snapshot(), {'layout': {'zoomed': False}}]) as api:
            dock.dock(follow=True)
        self.assertEqual(api.call_count, 2)

    def test_other_pane_zoom_is_preserved(self):
        with patch.object(dock, 'api', side_effect=[self.snapshot(same_tab=False), {'layout': {'zoomed': True}}]) as api:
            dock.dock(follow=True)
        self.assertEqual(api.call_count, 2)

    def test_zoom_restore_returns_focus_to_work(self):
        calls = []
        def api(method, **params):
            calls.append((method, params))
            if method == 'session.snapshot':
                return self.snapshot()
            if method == 'layout.export':
                return {'layout': {'zoomed': True, 'focused_pane_id': 'w2:p2'}}
            return {}
        with patch.object(dock, 'api', side_effect=api):
            dock.dock(toggle=True)
        self.assertIn(('pane.zoom', {'pane_id': 'w2:p2', 'mode': 'off'}), calls)
        self.assertEqual(calls[-1], ('pane.focus', {'pane_id': 'w2:p1'}))

    def test_cross_workspace_move_uses_new_pane_id(self):
        calls = []
        def api(method, **params):
            calls.append((method, params))
            if method == 'session.snapshot':
                return self.snapshot(same_tab=False)
            if method == 'layout.export':
                return {'layout': {'zoomed': False}}
            if method == 'pane.layout':
                return {'layout': {'panes': [{'pane_id': 'w2:p1', 'rect': {'height': 50}}]}}
            if method == 'pane.move':
                return {'changed': True, 'pane': {'pane_id': 'w2:p9'}}
            return {}
        with patch.object(dock, 'api', side_effect=api):
            dock.dock(follow=True)
        self.assertEqual(calls[-2][1]['pane_id'], 'w2:p9')
        self.assertTrue(all(method != 'pane.split' for method, _ in calls))
        self.refresh.assert_called_once_with('w2:p1', 'w2:t1')


class MusicResizeTests(unittest.TestCase):
    def test_navigation_race_does_not_steal_focus_or_signal(self):
        snapshot = {'snapshot': {'focused_tab_id': 'other', 'focused_pane_id': 'other:p1'}}
        with patch.object(dock.time, 'sleep'), patch.object(dock, 'api', return_value=snapshot) as api:
            with patch.object(dock.os, 'killpg') as kill:
                dock.refresh_work_pane('w2:p1', 'w2:t1')
        self.assertEqual(api.call_count, 1)
        kill.assert_not_called()

    def test_resize_redraw_targets_only_current_foreground_group(self):
        responses = [
            {'snapshot': {'focused_tab_id': 'w2:t1', 'focused_pane_id': 'w2:p1'}},
            {}, {'process_info': {'foreground_process_group_id': 9876}},
        ]
        with patch.object(dock.time, 'sleep'), patch.object(dock, 'api', side_effect=responses) as api:
            with patch.object(dock.os, 'getpgrp', return_value=1234), patch.object(dock.os, 'killpg') as kill:
                dock.refresh_work_pane('w2:p1', 'w2:t1')
        self.assertEqual(api.call_args_list[1].args, ('pane.focus',))
        kill.assert_called_once_with(9876, dock.signal.SIGWINCH)


if __name__ == '__main__':
    unittest.main()
