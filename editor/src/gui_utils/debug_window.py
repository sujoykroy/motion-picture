from gi.repository import Gtk
from ..commons import *
from ..gui_utils import NameValueComboBox

class DebugWindow(Gtk.Dialog):
    def __init__(self, parent, title="Viewer", width=400, height = 200):
        Gtk.Dialog.__init__(self, title, parent, 0,())
        self.set_default_size(width, height)
        self.connect("delete-event", self.quit)

        self.master_editor = parent
        box = self.get_content_area()

        code_editor_box = Gtk.HBox()
        box.pack_start(code_editor_box, expand=True, fill=True, padding=5)

        self.code_editor = Gtk.TextView()
        code_editor_box.pack_start(self.code_editor, expand=True, fill=True, padding=5)

        execute_button = Gtk.Button("Run")
        code_editor_box.pack_start(execute_button, expand=False, fill=False, padding=5)
        execute_button.connect("clicked", self.execute_button_clicked)

        #self.code_result = Gtk.TextView()
        #box.pack_start(self.code_result, expand=True, fill=True, padding=5)

        self.show_all()

    def execute_button_clicked(self, widget):
        text_buffer = self.code_editor.get_buffer()
        code_text = text_buffer.get_text(text_buffer.get_start_iter(),
                text_buffer.get_end_iter(), False)
        code_object = compile(code_text, '', 'exec')
        result = eval(code_object)
        #self.code_result.get_buffer().set_text("{0}".format(result))

    def quit(self, widget, event):
        return
        self.master_editor.on_quit_debug_window()
