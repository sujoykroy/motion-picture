from tkinter import filedialog

class Dialog:
    def ask_for_project_file(open=True):
        filetypes = [("JSON", "*.json")]
        if open:
            project_filename = filedialog.askopenfilename(
                filetypes=filetypes, title="Select a project file to open")
        else:
            project_filename = filedialog.asksaveasfilename(
                filetypes=filetypes,
                title="Choose folder and write filename to save new project")
        if project_filename:
            root, ext = os.path.splitext(project_filename)
            if ext != ".json":
                project_filename += ".json"
        return project_filename

    def ask_for_image_files(self, image_types):
        image_files = filedialog.askopenfilenames(
            title="Select images to import",
            filetypes=(
                ("Images", image_types),
                ("All Files", "*.*")
            )
        )
        return image_files
