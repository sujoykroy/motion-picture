import unittest

from img2vid.geom import Polygon, Point
from img2vid.effects import ScalePan

class TestScalePan(unittest.TestCase):
    def test_no_scale(self):
        scale_pan = ScalePan(0.25, 0.25, Polygon([Point(0, 0), Point(1,1)]))

        rect = scale_pan.get_rect_at(frac=0, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 0)
        self.assertEqual(rect.y1, 0)
        self.assertEqual(rect.x2, 25)
        self.assertEqual(rect.y2, 25)

        rect = scale_pan.get_rect_at(frac=1, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 75)
        self.assertEqual(rect.y1, 75)
        self.assertEqual(rect.x2, 100)
        self.assertEqual(rect.y2, 100)

    def test_no_pan(self):
        scale_pan = ScalePan(0.25, 0.75, Polygon([Point(0, 0), Point(0,0)]))

        rect = scale_pan.get_rect_at(frac=0, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 0)
        self.assertEqual(rect.y1, 0)
        self.assertEqual(rect.x2, 25)
        self.assertEqual(rect.x2, 25)

        rect = scale_pan.get_rect_at(frac=1, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 0)
        self.assertEqual(rect.y1, 0)
        self.assertEqual(rect.x2, 75)
        self.assertEqual(rect.y2, 75)

    def test_simple_scale_and_pan(self):
        scale_pan = ScalePan(0.25, 0.75, Polygon([Point(0, 0), Point(1, 1)]))

        rect = scale_pan.get_rect_at(frac=0, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 0)
        self.assertEqual(rect.y1, 0)
        self.assertEqual(rect.x2, 25)
        self.assertEqual(rect.x2, 25)

        rect = scale_pan.get_rect_at(frac=1, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 25)
        self.assertEqual(rect.y1, 25)
        self.assertEqual(rect.x2, 100)
        self.assertEqual(rect.y2, 100)

        rect = scale_pan.get_rect_at(frac=0.5, bound_width=100, bound_height=100)
        self.assertEqual(rect.x1, 25)
        self.assertEqual(rect.y1, 25)
        self.assertEqual(rect.x2, 75)
        self.assertEqual(rect.y2, 75)

    def test_aspect_ratio(self):
        scale_pan = ScalePan(0.25, 0.75, Polygon([Point(0, 0), Point(1, 1)]))

        rect = scale_pan.get_rect_at(
            frac=0, bound_width=200, bound_height=100, aspect_ratio=16/9)
        self.assertEqual(rect.width/rect.height, 16/9)

if __name__ == "__main__":
    unittest.main()
