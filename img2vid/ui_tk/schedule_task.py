class ScheduleTask:
    def __init__(self, master, period, task, data={}):
        self._period = period
        self._task = task
        self._task_data = data
        self._master = master
        self._running = False
        self._should_stop = False

    @property
    def period(self):
        return self._period

    def _run(self):
        result = self._task(*self._task_data)
        if result and not self._should_stop:
            self._running = True
            self._master.after(self._period, self._run)
        else:
            self._running = False

    def start(self):
        self._should_stop = False
        if not self._running:
            self._master.after(0, self._run)

    def stop(self):
        self._should_stop = True

