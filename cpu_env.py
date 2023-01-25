import simpy
import random
import enum

class CPU(simpy.Resource):
    def __init__(self, waiting_queue, queue_list) -> None:
        super().__init__()
        self.waiting_queue = waiting_queue
        self.queue_list = queue_list

class Task:
    pid = 0

    class Priority(enum.Enum):
        LOW = 0
        NORMAL = 1
        HIGH = 2

    def __init__(self, arrival_time, service_time, priority) -> None:
        self.priority = Task.Priority(priority)
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.pid = Task.pid
        Task.pid += 1

class Priority_Queue:

    class Priority(enum.Enum):
        FCFS = 0
        RR_T2 = 1
        RR_T1 = 2
    
    def __init__(self, name, Q_time, priority) -> None:
        self.name = name
        self.priority = Priority_Queue.Priority(priority)
        self.tasks = []
        self.Q_time = Q_time
        # if Q_time == None:
        #     self.Round_Robin = False

    def enqueue(self, task):
        self.tasks.append(task)

    def dequeue(self):
        if self.tasks:
            return self.tasks.pop(0)
        else:
            return None

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

    def sort_tasks(self):
        self.tasks.sort(key= lambda x: x.priority.int * self.p + x.service_time * self.t)

    def dequeue(self, K):
        if self.tasks:
            count = min(self.length(), K)
            d_list = []
            for _ in range(count):
                d_list.append(self.tasks.pop())
            return d_list
        else:
            return None

    def length(self):
        return len(self.tasks)

def job_creator(_lambda, _mu, priority_weights, waiting_queue: Priority_Queue, env: simpy.Environment):
    while True:
        # pending_time = expon.rvs(scale= (1/_lambda), size=1)
        priority = random.choices(([p.value for p in Task.Priority]), weights=priority_weights, k=1)[0]
        pending_time = int(random.expovariate(_lambda))
        yield env.timeout(pending_time)
        arrival_time = env.now
        service_time = int(random.expovariate(1/_mu))
        task = Task(arrival_time, service_time, priority)
        waiting_queue.enqueue(task)

def job_loader(sleep_time, K, waiting_queue: Waiting_Queue, queue_list, env: simpy.Environment):
    while True:
        t = 0
        for q in queue_list:
            t += q.length()
        if t < K:
            waiting_queue.sort_tasks()
            new_tasks = waiting_queue.dequeue(K)
            queue_list[0].append(new_tasks)
        yield env.timeout(sleep_time)

# env = simpy.Environment()
# env.process(job_creator(1, 2, [0.7, 0.2, 0.1], Priority_Queue(), env))
# env.run(until = 50)
