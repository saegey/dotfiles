import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[2] / 'herdr/.local/bin/herdr-music-view'
loader = importlib.machinery.SourceFileLoader('music_view', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
view = importlib.util.module_from_spec(spec)
loader.exec_module(view)


class MusicViewTests(unittest.TestCase):
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
