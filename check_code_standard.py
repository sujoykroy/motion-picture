import sys
import os
import re
import subprocess
import tkinter as tk
from tkinter import simpledialog
import tkinter.scrolledtext as tkscrolledtext

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_NAMES = [ "\.git.*"]

class CodeStandardChecker(tk.Frame):
    def __init__(self, master, width=1000, height=400):
        super(CodeStandardChecker, self).__init__(master=master)
        self.master.resize(width, height)
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.pack(expand=1, fill=tk.BOTH)

        self.splitter = tk.PanedWindow(self, orient=tk.HORIZONTAL, relief=tk.SUNKEN)
        self.splitter.pack(fill=tk.BOTH, expand=1)

        self.left_panel = tk.Frame(self.splitter)
        self.splitter.add(self.left_panel, minsize=width/3)

        self.right_panel = tk.Frame(self.splitter)
        self.splitter.add(self.right_panel)

        self.file_list_label = tk.Label(self.left_panel, text="Files")
        self.file_list_label.pack(side=tk.TOP, fill=tk.X)

        self.file_list_frame = tk.Frame(self.left_panel)
        self.file_list_frame.columnconfigure(0, weight=1)
        self.file_list_frame.rowconfigure(0, weight=1)
        self.file_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.file_list_yscrollbar = tk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL)
        self.file_list_yscrollbar.grid(row=0, column=1, rowspan=2, sticky=tk.N+tk.S)

        self.file_list = tk.Listbox(self.file_list_frame)
        self.file_list.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.file_list.bind('<Double-Button-1>', self.run_pylint_on_selected_file)

        self.file_list_xscrollbar = tk.Scrollbar(self.file_list_frame, orient=tk.HORIZONTAL)
        self.file_list_xscrollbar.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)


        self.file_list.config(yscrollcommand=self.file_list_yscrollbar.set)
        self.file_list_yscrollbar.config(command=self.file_list.yview)
        self.file_list.config(xscrollcommand=self.file_list_xscrollbar.set)
        self.file_list_xscrollbar.config(command=self.file_list.xview)

        self.output_label = tk.Label(self.right_panel, text="Output")
        self.output_label.pack(side=tk.TOP, fill=tk.X)

        self.output_text = tkscrolledtext.ScrolledText(self.right_panel, height="5", width="40")
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.button_toolbar = tk.Frame(self)
        self.button_toolbar.pack(fill=tk.X)

        self.run_selected_button = tk.Button(self.button_toolbar,
                                             text="Run PyLint on Selected File",
                                             command=self.run_pylint_on_selected_file)
        self.run_selected_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.button_toolbar,
                                        text="Quit",
                                        command=self.on_window_close)
        self.quit_button.pack(side=tk.RIGHT)

        self.root_dir = os.path.join(THIS_DIR)
        self.filepaths = []
        self.load_files(self.root_dir, len(self.root_dir)+1)

    def load_files(self, root_dir, offset):
        for filepath in os.listdir(root_dir):
            if EXCLUDE_NAMES:
                exclude_it = False
                for exclude_name in EXCLUDE_NAMES:
                    if re.match(exclude_name, filepath):
                        exclude_it = True
                        break
                if exclude_it:
                    continue
            filepath = os.path.join(root_dir, filepath)
            if os.path.isdir(filepath):
                self.load_files(filepath, offset)
            else:
                root, ext = os.path.splitext(filepath)
                if ext == ".py":
                    self.filepaths.append(filepath)
                    self.file_list.insert(tk.END, filepath[offset:])

    def run_pylint(self, filepath):
        heading = "Running pylint:\nfile:{}\n".format(filepath)
        self.output_text.insert(tk.END, heading)

        args = "pylint {0}".format(filepath).split(" ")
        args.extend(["--rcfile", os.path.join(THIS_DIR, "pylintrc.ini")])
        process = subprocess.run(args, stdout=subprocess.PIPE)
        self.output_text.insert(tk.END, process.stdout)

    def run_pylint_on_selected_file(self, *args):
        self.run_selected_button["state"] = tk.DISABLED
        sel = self.file_list.curselection()[0]
        filepath = os.path.join(self.root_dir, self.filepaths[sel])
        self.output_text.delete("1.0", tk.END)
        self.run_pylint(filepath)
        self.run_selected_button["state"] = tk.NORMAL

    def on_window_close(self):
        self.master.destroy()

class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Img2Vid Code Standard Checker")

    def show_at_center(self, use_req=False):
        self.withdraw()
        self.update_idletasks()
        if use_req:
            x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
            y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
        else:
            x = (self.winfo_screenwidth() - self.winfo_width()) / 2
            y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()
        self.update_idletasks()

    def resize(self, width, height):
        self.geometry('{}x{}'.format(width, height))

tk_root = Root()
checker = CodeStandardChecker(tk_root)
tk_root.show_at_center()
tk_root.show_at_center()#call twice
checker.mainloop()
try:
    sys.exit()
except:
    pass


