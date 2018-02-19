import numpy
from img2vid.renderer import ImageRenderer

class ImageUtils:
    @staticmethod
    def get_pixel_at(image, x_pos, y_pos):
        img_buffer = numpy.array(image, dtype=numpy.uint8)
        return img_buffer[int(y_pos), int(x_pos), :]

    def create_memory_image_file(self, width, height, fil_color="#FFFFFF"):
        file_ob = tempfile.SpooledTemporaryFile()
        self.temp_files.append(file_ob);
        image = ImageRenderer.create_blank(width, height, fil_color)
        image.save(file_ob.name, "PNG")
        return file_ob
