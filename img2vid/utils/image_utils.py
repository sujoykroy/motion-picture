import tempfile

import PIL
import PIL.Image

import numpy
import wand.image
import wand.drawing
import wand.color

from ..geom import Rectangle
from ..analysers import ImageAnalyser

from .video_cache import VideoCache

class ImageUtils:
    PIXEL_PER_INCH = "pixelsperinch"

    EXIF_TO_RENDERER_ORIENTATION = {
        '2' : PIL.Image.FLIP_LEFT_RIGHT,
        '3' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.FLIP_TOP_BOTTOM],
        '4' : PIL.Image.FLIP_TOP_BOTTOM,
        '5' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_270],
        '6' : PIL.Image.ROTATE_270,
        '7' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_90],
        '8' : PIL.Image.ROTATE_90
    }

    @classmethod
    def fetch_video_frame(cls, filepath, time_pos, crop, wand_image=False):
        frame = VideoCache.get_video_clip(filepath).reader.get_frame(time_pos)
        image = PIL.Image.fromarray(frame.copy()).convert("RGBA")
        if crop:
            image = image.crop((crop.x1, crop.y1, crop.x2, crop.y2))
        if wand_image:
            image_file = tempfile.SpooledTemporaryFile()
            image.save(image_file, format="PNG")
            image_file.seek(0)
            image = wand.image.Image(file=image_file, format="png")
            image_file.close()
        return image

    @classmethod
    def fetch_image(cls, filepath, crop, wand_image=False):
        exif = ImageAnalyser.get_exif(filepath)
        exif_orient = exif.get(ImageAnalyser.KEY_EXIF_ORIENTATION)

        if wand_image:
            image = wand.image.Image(filename=filepath)
            image = cls.reverse_orient(image, exif_orient=exif_orient)
            if crop:
                image.crop(int(crop.x1), int(crop.y1),
                           int(crop.x2), int(crop.y2))
        else:
            image = PIL.Image.open(filepath).convert("RGBA")
            image = cls.reverse_orient(image, exif_orient=exif_orient)
            if crop:
                image = image.crop((crop.x1, crop.y1, crop.x2, crop.y2))
        return image

    @classmethod
    def fit_inside(cls, image, width, height):
        scale_x = width/image.width
        scale_y = height/image.height
        scale = min(scale_x, scale_y)
        image = cls.resize(
            image,
            width=int(image.width*scale),
            height=int(image.height*scale))
        return image

    @classmethod
    def fit_full(cls, image, width, height):
        """"This will make the image fit given width and height.
        To keep aspcet ratio, it will automactically cut of some boder zones."""

        max_scale = max(width/image.width, height/image.height)
        image = cls.same_scale(image, max_scale)
        rect = Rectangle()
        rect.set_cxy_wh(
            image.width/2, image.height/2,
            width, height)
        return cls.crop(image, rect)

    @classmethod
    def same_scale(cls, image, scale):
        return cls.resize(
            image, int(image.width*scale), int(image.height*scale))

    @staticmethod
    def resize(image, width, height):
        if isinstance(image, wand.image.Image):
            image = wand.image.Image(image=image)
            image.resize(width, height)
        else:
            image = image.resize((width, height), resample=True)
        return image

    @classmethod
    def crop(cls, image, rect):
        if isinstance(image, wand.image.Image):
            image.crop(
                int(rect.x1), int(rect.y1), int(rect.x2), int(rect.y2))
        else:
            image = image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
        return image

    @staticmethod
    def wand2pil(wand_image):
        wand_image.format = "png"
        temporary_file = tempfile.SpooledTemporaryFile()

        wand_image.save(file=temporary_file)

        pil_image = PIL.Image.open(temporary_file)
        pil_image.load()
        temporary_file.close()

        return pil_image.convert("RGBA")

    @classmethod
    def reverse_orient(cls, image, exif_orient=None, renderer_orient=None):
        if exif_orient:
            renderer_orient = \
                cls.EXIF_TO_RENDERER_ORIENTATION.get(exif_orient, None)
        if not renderer_orient:
            return image
        if isinstance(renderer_orient, list):
            for orient in renderer_orient:
                image = cls.reverse_orient(image, renderer_orient=orient)
            return image
        if not hasattr(image, "flop"):#for PIL Image
            image = image.transpose(renderer_orient)
        else:
            image = wand.image.Image(image)
            if renderer_orient == PIL.Image.FLIP_LEFT_RIGHT:
                image.flop()
            elif renderer_orient == PIL.Image.FLIP_TOP_BOTTOM:
                image.flip()
            elif renderer_orient == PIL.Image.ROTATE_90:
                image.rotate(-90)
            elif renderer_orient == PIL.Image.ROTATE_270:
                image.rotate(90)
        return image

    @staticmethod
    def create_blank(width, height, fill_color):
        image = PIL.Image.new("RGBA", (int(width), int(height)), fill_color)
        return image

    @staticmethod
    def set_alpha(image, alpha):
        image = image.convert("RGBA")
        img_buffer = numpy.array(image, dtype=numpy.uint8)
        img_buffer[:, :, 3] = img_buffer[:, :, 3]*alpha
        img_buffer.dtype = numpy.uint8
        image = PIL.Image.fromarray(img_buffer)
        return image

    @staticmethod
    def get_pixel_at(image, x_pos, y_pos):
        img_buffer = numpy.array(image, dtype=numpy.uint8)
        return img_buffer[int(y_pos), int(x_pos), :]
