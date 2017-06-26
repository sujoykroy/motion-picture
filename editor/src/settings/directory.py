import os

class Directory(object):
    All = []

    @staticmethod
    def get_full_path(path):
        if not path:
            return path
        directory = os.path.dirname(path)
        if not directory:
            for folder in Directory.All:
                full_path = os.path.join(folder, path)
                if os.path.isfile(full_path):
                    return full_path
        return path

    @staticmethod
    def add_new(path):
        if not path:
            return
        directory = os.path.dirname(path)
        if directory not in Directory.All:
            Directory.All.append(directory)

