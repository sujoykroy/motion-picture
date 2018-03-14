import unittest

from img2vid.geom import Rectangle
from img2vid.slides import TextSlide, ImageSlide
from img2vid.slides.caption import Caption
from img2vid.renderer.render_info import RenderInfo
from img2vid.renderer import ImageRenderer

class TestSerialization(unittest.TestCase):
    def test_text_slide_json(self):
        slide = TextSlide(caption=Caption({'text': 'Some text'}))
        new_slide = TextSlide.create_from_json(slide.get_json())
        self.assertEqual(new_slide.caption.text, "Some text")

        slide = TextSlide()
        new_slide = TextSlide.create_from_json(slide.get_json())
        self.assertEqual(new_slide.caption.text, "")

    def test_image_slide_json(self):
        slide = ImageSlide(filepath="somepath")
        slide.get_caption("top").text = "Some top text"
        slide.get_caption("center").text = "Some center text"
        slide.get_caption("bottom").text = "Some bottom text"

        new_slide = ImageSlide.create_from_json(slide.get_json())
        self.assertEqual(new_slide.filepath, "somepath")
        self.assertEqual(new_slide.get_caption('top').text, "Some top text")
        self.assertEqual(new_slide.get_caption('center').text, "Some center text")
        self.assertEqual(new_slide.get_caption('bottom').text, "Some bottom text")

    def test_render_info_json(self):
        info = RenderInfo(
            image=ImageRenderer.create_blank(14, 23, "#000000"),
            editable_rect=Rectangle(10,20, 30, 40),
            orig_image_scale=2)

        new_info = RenderInfo.create_from_json(info.get_json())
        self.assertEqual(new_info.editable_rect.x1, 10)
        self.assertEqual(new_info.orig_image_scale, 2)
        self.assertEqual(new_info.image.width, 14)
        self.assertEqual(new_info.image.height, 23)

if __name__ == "__main__":
    unittest.main()
