import unittest
from types import SimpleNamespace
import PIL.ImageDraw

from img2vid.geom import Point , Rectangle
from img2vid.ui_tk.image_fitter import ImageFitter
from img2vid.renderer.render_info import RenderInfo
from img2vid.renderer import ImageRenderer

from utils import ImageUtils

class TestImageEditor(unittest.TestCase):
    def test_matching_rect_in_edit_rect(self):
        fitter = ImageFitter()
        edit_rect = Rectangle(10, 20, 200, 300)
        image = ImageRenderer.create_blank(500, 600, "#000000")
        render_info = RenderInfo(image, edit_rect)
        fitter.render_info = render_info
        screen_config = SimpleNamespace(width=900, height=700)
        screen_size = Point(90, 70)
        fitter.build_screen_area(screen_size.x, screen_size.y, screen_config, auto_fit=False)
        fitter.fit(build_tk=False)
        rev_rect = fitter.reverse_transform_rect(fitter.rects.editable)
        self.assertEqual(rev_rect.x1, 0)
        self.assertEqual(rev_rect.y1, 0)
        self.assertEqual(rev_rect.x2, edit_rect.width)
        self.assertEqual(rev_rect.y2, edit_rect.height)

        percent_rect = Rectangle(.1, .2, .5, .6)
        orig_rect = percent_rect.copy()
        orig_rect.scale(edit_rect.width, edit_rect.height)

        fitter_rect = percent_rect.copy()
        fitter_rect.scale(fitter.rects.editable.width, fitter.rects.editable.height)
        fitter_rect.translate(Point(fitter.rects.editable.x1, fitter.rects.editable.y1))
        rev_rect = fitter.reverse_transform_rect(fitter_rect)
        self.assertEqual(round(rev_rect.x1), round(orig_rect.x1))
        self.assertTrue(round(rev_rect.y1), round(orig_rect.y1))
        self.assertEqual(round(rev_rect.x2), round(orig_rect.x2))
        self.assertEqual(round(rev_rect.y2), round(orig_rect.y2))

    def test_image_crop(self):
        rect = Rectangle(10, 20, 100, 200)
        image = ImageRenderer.create_blank(500, 600, "#000000")
        draw = PIL.ImageDraw.Draw(image)
        color = "#05FFFF"
        draw.rectangle([rect.x1, rect.y1, rect.x2, rect.y2], fill=color, outline=color)

        cropped = image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
        self.assertEqual(ImageUtils.get_pixel_at(cropped, 0, 0)[0], 5)

if __name__ == "__main__":
    unittest.main()
