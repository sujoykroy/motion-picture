import numpy

class ImageUtils:
    @staticmethod
    def get_pixel_at(image, x_pos, y_pos):
        img_buffer = numpy.array(image, dtype=numpy.uint8)
        return img_buffer[int(y_pos), int(x_pos), :]
