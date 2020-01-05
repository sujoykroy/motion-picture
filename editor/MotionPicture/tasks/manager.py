class TaskManager(object):
    MAX_TASK_COUNT = 20

    def __init__(self):
        self.tasks = []
        self.index = 0

    def is_empty(self):
        return len(self.tasks) == 0

    def add_task(self, task):
        del self.tasks[self.index:]
        self.tasks.append(task)
        if len(self.tasks)> self.MAX_TASK_COUNT:
            del self.tasks[0:len(self.tasks)-self.MAX_TASK_COUNT]
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

