from PIL import ImageTk

from commons import Point, Rectangle

class CanvasImage:
    def __init__(self, image, outer_area):
        sx = outer_area.x/image.width
        sy = outer_area.y/image.height
        self.scale = min(sx, sy)

        image_size = Point(
                int(image.width*self.scale), int(image.height*self.scale))
        self.offset = Point(
                (outer_area.x-image_size.x)*0.5,
                (outer_area.y-image_size.y)*0.5)

        self.bound_rect = Rectangle(self.offset.x, self.offset.y,
                                    self.offset.x + image_size.x,
                                    self.offset.y + image_size.y)
        self.image = image.resize((image_size.x, image_size.y), resample=True)
        self.tk_image = ImageTk.PhotoImage(image=self.image)
