import tkinter as tk

from .frame import Frame

class SlideNavigator(Frame):
    def __init__(self, master):
        super().__init__(
            master=master,
            event_names=['move_slide'])

        self.widgets.prev_btn = tk.Button(
            self.base, text="<<Prev", command=self._move_prev)
        self.widgets.prev_btn.pack(side=tk.LEFT)

        self.widgets.next_btn = tk.Button(
            self.base, text="Next>>", command=self._move_next)
        self.widgets.next_btn.pack(side=tk.RIGHT)

        self.widgets.slide_label = tk.Label(self.base, text="0/0")
        self.widgets.slide_label.pack(anchor=tk.CENTER)

    def _move_prev(self):
        self.events.move_slide.fire(incre=-1)

    def _move_next(self):
        self.events.move_slide.fire(incre=1)

    def set_info(self, cur_index, total):
        self.widgets.slide_label["text"] = "{0}/{1}".format(cur_index+1, total)
