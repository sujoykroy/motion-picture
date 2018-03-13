import unittest

from img2vid.geom import Rectangle
from img2vid.slides import TextSlide, ImageSlide
from img2vid.slides.caption import Caption

class TestSlideJsons(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
