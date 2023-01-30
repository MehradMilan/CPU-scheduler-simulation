import enum
import simpy

class Priority_Queue:

    class Priority(enum.Enum):
        Round_Robin_T1 = 0
        Round_Robin_T2 = 1
        FCFS = 2
    
    def __init__(self, name, Q_time, priority) -> None:
        self.name = name
        self.priority = Priority_Queue.Priority(priority)
        self.tasks = []
        self.Q_time = Q_time

    def enqueue(self, task):
        self.tasks.append(task)
        task.current_queue = self

    def dequeue(self):
        if self.tasks:
            return self.tasks.pop(0)
        else:
            return None

    def remove(self, task):
        self.tasks.remove(task)

    def length(self):
        return len(self.tasks)

class Waiting_Queue:

    def __init__(self, name, p, t) -> None:
        self.p = p
        self.t = t
        self.name = name
        self.tasks = []

    def enqueue(self, task):
        self.tasks.append(task)
        task.current_queue = self

    def sort_tasks(self):
        self.tasks.sort(key= lambda x: x.priority.value * self.p + x.service_time * self.t)

    def dequeue(self, K):
        if self.tasks:
            count = min(self.length(), K)
            d_list = []
            for _ in range(count):
                d_list.append(self.tasks.pop())
            return d_list
        else:
            return None

    def remove(self, task):
        self.tasks.remove(task)

    def length(self):
        return len(self.tasks)

class Task:
    pid = 1
    all_tasks = []

    class Priority(enum.Enum):
        LOW = 0
        NORMAL = 1
        HIGH = 2

    def __init__(self, arrival_time, service_time, max_timeout, priority) -> None:
        self.priority = Task.Priority(priority)
        self.service_time = service_time
        self.remaining_time = self.service_time
        self.arrival_time = arrival_time
        self.max_timeout = max_timeout
        self.is_finished = False
        self.is_timeout = False
        self.init_spend_times()
        self.pid = Task.pid
        Task.pid += 1
        Task.all_tasks.append(self)
        self.ss = None
        self.current_queue = None

    def __str__(self) -> str:
        return "Task " + str(self.pid) + " " + str(self.spend_times) + " " + str(self.is_timeout) + " " + str(self.is_finished)

    def start_starving(self, env):
        try:
            yield env.timeout(self.max_timeout)
            print(str(env.now) + " Task " + str(self.pid) + " is timeout" + " from " + self.current_queue.name)
            self.throw_out(env.now)
            self.ss = None
        except simpy.Interrupt:
            self.ss = None

    def throw_out(self, now):
        self.is_timeout = True
        self.update_queue_exit_time(self.current_queue.name, now)
        self.current_queue.remove(self)
        self.current_queue = None
    
    def init_spend_times(self):
        self.spend_times = {}
        self.spend_times["Waiting_Queue"] = (0, 0)
        for pq in Priority_Queue.Priority:
            self.spend_times[pq.name] = (0, 0)

    def update_queue_enter_time(self, queue_name, enter_time):
        self.spend_times[queue_name] = (enter_time, self.get_spend_time(queue_name)[1])

    def update_queue_exit_time(self, queue_name, exit_time):
        self.spend_times[queue_name] = (self.get_spend_time(queue_name)[0], exit_time)
    
    def update_spend_times(self, queue_name, enter_time, exit_time):
        self.spend_times[queue_name] = (enter_time, exit_time)

    def get_spend_time(self, queue_name):
        return self.spend_times[queue_name]

    def get_total_spend_time(self):
        total = 0
        for pq in Priority_Queue.Priority:
            total += self.spend_times[pq][1] - self.spend_times[pq][0]
        return total