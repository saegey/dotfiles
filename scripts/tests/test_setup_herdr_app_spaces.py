import json
from pathlib import Path
import runpy
import unittest

setup = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'setup-herdr-app-spaces'))


class SidebarLayoutTests(unittest.TestCase):
    def test_preserves_music_and_sidebar_geometry(self):
        layout = {'id': 'root', 'children': [
            {'id': 'spaces', 'size': {'px': 268}, 'content': {'mod': 'spaces', 'props': {'custom': True}}},
            {'id': 'music', 'content': {'mod': 'music-dock'}},
        ]}
        original = json.dumps(layout)
        result = setup['spaces_layout'](layout)
        self.assertEqual(json.dumps(layout), original)
        self.assertEqual(result['children'][0]['content'], {'mod': 'dotfiles-spaces', 'props': {'custom': True}})
        self.assertEqual(result['children'][0]['size'], {'px': 268})
        self.assertEqual(result['children'][1], layout['children'][1])
        self.assertEqual(setup['spaces_layout'](result), result)

    def test_rejects_missing_or_ambiguous_sidebar(self):
        for layout in ({}, {'children': [{'content': {'mod': 'spaces'}}, {'content': {'mod': 'spaces'}}]}):
            with self.assertRaises(ValueError):
                setup['spaces_layout'](layout)


if __name__ == '__main__':
    unittest.main()
