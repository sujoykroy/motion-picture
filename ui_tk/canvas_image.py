from PIL import ImageTk

from commons import Point, Rectangle

class CanvasImage:
    def __init__(self, image, outer_rect):
        outer_width = outer_rect.get_width()
        outer_height = outer_rect.get_height()

        sx = outer_width/image.width
        sy = outer_height/image.height
        self.scale = min(sx, sy)

        image_size = Point(int(image.width*self.scale), int(image.height*self.scale))
        self.offset = Point(
                (outer_width-image_size.x)*0.5, (outer_height-image_size.y)*0.5)

        self.offset.add(Point(outer_rect.x1, outer_rect.y1))

        self.bound_rect = Rectangle(self.offset.x, self.offset.y,
                                    self.offset.x + image_size.x,
                                    self.offset.y + image_size.y)
        self.image = image.resize((image_size.x, image_size.y), resample=True)
        self.tk_image = ImageTk.PhotoImage(image=self.image)

    def canvas2image(self, rect):
        rect = rect.copy()
        rect.translate(self.offset, sign=-1)
        rect.scale(1/self.scale, 1/self.scale)
        return rect
