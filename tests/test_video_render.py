import unittest
import tempfile

from utils import ImageUtils

from img2vid.geom import Rectangle
from img2vid.configs import AppConfig
from img2vid.slides import Project, TextSlide
from img2vid.renderer import ImageRenderer, VideoRenderer
from img2vid.effects import FadeIn, FadeOut, ScalePan

class TestVideoRenderer(unittest.TestCase):

    def setUp(self):
        AppConfig.OLD_FILENAME = AppConfig.FILENAME
        self.temp_files = []

    def tearDown(self):
        for temp_file in self.temp_files:
            temp_file.close()
        del self.temp_files[:]
        AppConfig.FILENAME = AppConfig.OLD_FILENAME

    def create_mock_app_config(self):
        file_ob = tempfile.NamedTemporaryFile()
        self.temp_files.append(file_ob);
        AppConfig.FILENAME = file_ob.name
        return AppConfig()

    def create_mock_image_file(self, width, height, fil_color="#FFFFFF"):
        file_ob = tempfile.NamedTemporaryFile()
        self.temp_files.append(file_ob);
        image = ImageRenderer.create_blank(width, height, fil_color)
        image.save(file_ob.name, "PNG")
        return file_ob

    def test_scale_pan_image_slide(self):
        project = Project()

        temp_file = self.create_mock_image_file(100, 200)
        project.add_image_files([temp_file.name])

        app_config = self.create_mock_app_config()

        video_renderer = VideoRenderer.create_from_project(project, app_config)
        self.assertEqual(
            video_renderer.slices[0].start_time, 0)
        self.assertEqual(
            video_renderer.slices[0].end_time, app_config.image.duration)

        slide_slice = video_renderer.slices[0]
        self.assertEqual(len(slide_slice.effect_slices), 1)

        effect_slice = slide_slice.effect_slices[0]
        self.assertEqual(effect_slice.start_time, 0)
        self.assertEqual(effect_slice.end_time, slide_slice.duration)

        image = video_renderer.get_image_at(0)
        self.assertEqual(image.width/image.height, app_config.video_render.aspect_ratio)
        self.assertEqual(image.width, app_config.video_render.width)
        self.assertEqual(image.height, app_config.video_render.height)

    def test_caption_image_slide(self):
        project = Project()

        temp_file = self.create_mock_image_file(100, 200)
        project.add_image_files([temp_file.name])
        project.slides[0].text = "Some Caption"

        app_config = self.create_mock_app_config()

        video_renderer = VideoRenderer.create_from_project(project, app_config)
        self.assertEqual(
            video_renderer.slices[0].start_time, 0)
        self.assertEqual(
            video_renderer.slices[0].end_time, app_config.image.duration)

        slide_slice = video_renderer.slices[0]
        self.assertEqual(len(slide_slice.effect_slices), 0)

        image = video_renderer.get_image_at(0)
        self.assertEqual(image.width/image.height, app_config.video_render.aspect_ratio)
        self.assertEqual(image.width, app_config.video_render.width)
        self.assertEqual(image.height, app_config.video_render.height)


    def test_fade_in_out_image_slide(self):
        project = Project()
        app_config = self.create_mock_app_config()

        temp_file = self.create_mock_image_file(100, 200, "#FFFFFF")
        project.add_image_files([temp_file.name])

        project.slides[0].add_effect(FadeIn, dict(duration=2))
        project.slides[0].add_effect(FadeOut, dict(duration=3))

        video_renderer = VideoRenderer.create_from_project(project, app_config)
        slide_slice = video_renderer.slices[0]

        self.assertEqual(
            slide_slice.effect_slices[2].effect.TYPE_NAME, FadeIn.TYPE_NAME)
        self.assertEqual(slide_slice.effect_slices[2].start_time, 0)
        self.assertEqual(slide_slice.effect_slices[2].end_time, 2)

        self.assertEqual(
            slide_slice.effect_slices[0].effect.TYPE_NAME, ScalePan.TYPE_NAME)
        self.assertEqual(slide_slice.effect_slices[0].start_time, 0)
        self.assertEqual(
            slide_slice.effect_slices[0].end_time, app_config.image.duration+2+3)

        self.assertEqual(
            slide_slice.effect_slices[1].effect.TYPE_NAME, FadeOut.TYPE_NAME)
        self.assertEqual(
            slide_slice.effect_slices[1].start_time, app_config.image.duration+2)
        self.assertEqual(
            slide_slice.effect_slices[1].end_time, app_config.image.duration+2+3)

        self.assertEqual(slide_slice.start_time, 0)
        self.assertEqual(slide_slice.end_time, app_config.image.duration+5)

        self.assertEqual(len(slide_slice.effect_slices), 3)

        image = video_renderer.get_image_at(0)
        self.assertEqual(image.width/image.height, app_config.video_render.aspect_ratio)
        self.assertEqual(image.width, app_config.video_render.width)
        self.assertEqual(image.height, app_config.video_render.height)

        #Fade in checking
        image = video_renderer.slices[0].get_image_at(0, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 0)

        image = video_renderer.slices[0].get_image_at(1, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 127)

        image = video_renderer.slices[0].get_image_at(2, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 255)

        #Fade out checking
        image = video_renderer.slices[0].get_image_at(app_config.image.duration+2, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 255)

        image = video_renderer.slices[0].get_image_at(app_config.image.duration+2+1.5, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 127)

        image = video_renderer.slices[0].get_image_at(app_config.image.duration+2+3, app_config)
        pixel_value = ImageUtils.get_pixel_at(image, 0, 0)
        self.assertEqual(pixel_value[3], 0)

    def test_on_fade_in_image_slide(self):
        project = Project()
        app_config = self.create_mock_app_config()

        temp_file = self.create_mock_image_file(100, 200, "#FFFFFF")
        project.add_image_files([temp_file.name])
        project.slides[0].text = "Caption"
        project.slides[0].add_effect(FadeIn, dict(duration=2))

        video_renderer = VideoRenderer.create_from_project(project, app_config)
        slide_slice = video_renderer.slices[0]

        self.assertEqual(
            slide_slice.effect_slices[0].effect.TYPE_NAME, FadeIn.TYPE_NAME)
        self.assertEqual(slide_slice.effect_slices[0].start_time, 0)
        self.assertEqual(slide_slice.effect_slices[0].end_time, 2)

        self.assertEqual(slide_slice.end_time, app_config.image.duration+2)

    def test_cropped_image_slides(self):
        project = Project()

        temp_file = self.create_mock_image_file(100, 200)
        project.add_image_files([temp_file.name])
        project.add_slide(project.slides[0].crop(Rectangle(10, 10, 20, 20)))
        project.remove_slide(0)

        app_config = self.create_mock_app_config()

        video_renderer = VideoRenderer.create_from_project(project, app_config)
        slide_slice = video_renderer.slices[0]
        image = slide_slice.get_image_at(0, app_config)
        self.assertEqual(image.width, app_config.video_render.width)
        self.assertEqual(image.height, app_config.video_render.height)
if __name__ == "__main__":
    unittest.main()
