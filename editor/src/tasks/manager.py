class TaskManager(object):
    def __init__(self):
        self.tasks = []
        self.index = 0

    def is_empty(self):
        return len(self.tasks) == 0

    def add_task(self, task):
        del self.tasks[self.index:]
        self.tasks.append(task)
        self.index = len(self.tasks)

    def remove_task(self, task):
        index = self.tasks.index(task)
        self.tasks.remove(task)
        if self.index>index:
            self.index -= 1

    def get_undo_task(self):
        if self.index<1: return None
        self.index -= 1
        task = self.tasks[self.index]
        return task

    def get_redo_task(self):
        if self.index>=len(self.tasks): return None
        task = self.tasks[self.index]
        self.index += 1
        return task

