import cProfile
import pstats
import io
import tempfile
import time

import tkinter as tk
import tkinter.scrolledtext as tkscrolledtext

try:
    import objgraph
except ImportError:
    objgraph = None

from img2vid.ui_tk.base_app import BaseApp
from img2vid.configs import AppConfig
from img2vid.slides import Project
from img2vid.renderer import VideoRenderer, ImageRenderer

def create_temp_image_file(width, height, fil_color="#FFFFFF"):
    file_ob = tempfile.NamedTemporaryFile()
    image = ImageRenderer.create_blank(width, height, fil_color)
    image.save(file_ob.name, "PNG")
    return file_ob

class ProfilingWindow(tk.Frame):
    def __init__(self, master, width=1000, height=400):
        super(ProfilingWindow, self).__init__(master=master)
        self.master.resize(width, height)
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.pack(expand=1, fill=tk.BOTH)

        self.splitter = tk.PanedWindow(self, orient=tk.HORIZONTAL, relief=tk.SUNKEN)
        self.splitter.pack(fill=tk.BOTH, expand=1)

        self.left_panel = tk.Frame(self.splitter)
        self.splitter.add(self.left_panel)

        self.right_panel = tk.Frame(self.splitter)
        self.splitter.add(self.right_panel)

        self.tests_label = tk.Label(self.left_panel, text="Tests")
        self.tests_label.pack(side=tk.TOP, fill=tk.X)

        self.test_list = tk.Listbox(self.left_panel)
        self.test_list.pack(fill=tk.BOTH, expand=1)
        self.test_list.bind('<Double-Button-1>', self.run_selected_test)

        self.output_label = tk.Label(self.right_panel, text="Output")
        self.output_label.pack(side=tk.TOP, fill=tk.X)

        self.output_text = tkscrolledtext.ScrolledText(self.right_panel, height="5", width="40")
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.button_toolbar = tk.Frame(self)
        self.button_toolbar.pack(fill=tk.X)

        self.run_selected_button = tk.Button(
            self.button_toolbar, text="Run selected test",
            command=self.run_selected_test)
        self.run_selected_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.button_toolbar,
                                        text="Quit",
                                        command=self.on_window_close)
        self.quit_button.pack(side=tk.RIGHT)


        self.test_names = [("Simple Video Render", self.test_video_render)]
        self.load_test_list()

    def load_test_list(self):
        for test_name, _ in self.test_names:
            self.test_list.insert(tk.END, test_name)

    def run_selected_test(self, *args):
        sel = self.test_list.curselection()[0]
        test_name = self.test_names[sel][0]
        test_func = self.test_names[sel][1]

        self.output_text.delete("1.0", tk.END)

        self.output_text.insert(tk.END, self.get_growth_stat())

        self.output_text.insert(tk.END, "Execution of '{}' is started.\n".format(test_name))
        self.master.update_idletasks()
        start_time = time.time()
        result = test_func()
        duration = time.time()-start_time
        self.output_text.insert(tk.END, result)
        self.output_text.insert(
            tk.END,
            "Execution of '{0}' is completed in {1:.2} sec.\n".format(
                test_name, duration))

        self.output_text.insert(tk.END, self.get_growth_stat())

    def get_growth_stat(self):
        if not objgraph:
            return ""
        stream = io.StringIO()
        objgraph.show_growth(file=stream)
        result = "Objgraph Growth Stat\n"
        result += "====================\n"
        result += stream.getvalue()
        return result

    def on_window_close(self):
        self.master.destroy()

    def test_video_render(self):
        prf = cProfile.Profile()
        prf.enable()

        self.render_simple()

        prf.disable()
        stream = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(prf, stream=stream).sort_stats(sortby)
        ps.print_stats()

        return stream.getvalue()

    def render_simple(self):
        project = Project()
        image_file = create_temp_image_file(100, 100)
        project.add_image_files([image_file.name])

        app_config = AppConfig("fake.ini")
        app_config.image.params["duration"] = 1
        video_renderer = VideoRenderer.create_from_project(project, app_config)

        dest_file = tempfile.NamedTemporaryFile(suffix=".mov")
        video_renderer.make_video(dest_file.name)


base_app = BaseApp("Profiling", 800, 600)
profiler = ProfilingWindow(base_app)
base_app.show_at_center()
profiler.mainloop()
try:
    sys.exit()
except:
    pass
