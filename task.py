class Task():
    def __init__(self, offset, wcet, period, priority, name):
        self.offset = offset
        self.wcet = wcet
        self.period = period
        self.priority = priority
        self.name = name

        self.completed = True
        self.already_done = 0
        self.job_nb = 0
