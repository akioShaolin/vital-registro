import unittest

from vitalregistro.insets import content_insets


class InsetsTests(unittest.TestCase):
    def test_edge_to_edge_reserves_status_and_navigation_bars(self):
        self.assertEqual(content_insets((720, 1600), (0, 0, 720, 1600), (0, 32, 720, 1510)),
                         (0, 32, 0, 90))

    def test_os_already_resized_view_does_not_get_double_padding(self):
        self.assertEqual(content_insets((720, 1600), (0, 32, 720, 1510), (0, 32, 720, 1510)),
                         (0, 0, 0, 0))

    def test_keyboard_overlap_and_scaling(self):
        self.assertEqual(content_insets((720, 1600), (0, 32, 720, 1510), (0, 32, 720, 1000), (.5, .5)),
                         (0, 0, 0, 255))

    def test_keyboard_already_excluded_and_side_cutout(self):
        self.assertEqual(content_insets((1600, 720), (0, 0, 1600, 400), (40, 0, 1560, 400)),
                         (40, 0, 40, 0))
