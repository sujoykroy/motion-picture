class UtilsTk:
    @staticmethod
    def show_widget_at_center(widget):
        """Shows the widget at the center of the screen."""
        for _ in range(2):
            widget.withdraw()
            widget.update_idletasks()
            left = (widget.winfo_screenwidth() - widget.winfo_width()) / 2
            top = (widget.winfo_screenheight() - widget.winfo_height()) / 2
            widget.geometry("+%d+%d" % (left, top))
            widget.deiconify()
            widget.update_idletasks()
