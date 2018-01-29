import PIL
from wand.image import Image as WandImage

EXIF_ORIENTATION = {
    '2' : PIL.Image.FLIP_LEFT_RIGHT,
    '3' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.FLIP_TOP_BOTTOM],
    '4' : PIL.Image.FLIP_TOP_BOTTOM,
    '5' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_270],
    '6' : PIL.Image.ROTATE_270,
    '7' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_90],
    '8' : PIL.Image.ROTATE_90
}

def reverse_orient(image, exif_orient=None, orientation=None):
    if exif_orient:
        orientation = EXIF_ORIENTATION.get(exif_orient, None)
    if not orientation:
        return image
    if isinstance(orientation, list):
        for orient in orientation:
           image = reverse_orient(image, orientation=orient)
        return image
    if not hasattr(image, "flop"):
        image = image.transpose(orientation)
    else:
        image = WandImage(image)
        if orientation == PIL.Image.FLIP_LEFT_RIGHT:
            image.flop()
        elif orientation == PIL.Image.FLIP_TOP_BOTTOM:
            image.flip()
        elif orientation == PIL.Image.ROTATE_90:
            image.rotate(-90)
        elif orientation == PIL.Image.ROTATE_270:
            image.rotate(90)
    return image

