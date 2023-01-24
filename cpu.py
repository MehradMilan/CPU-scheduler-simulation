import simpy
import random
from scipy.stats import expon
import enum

class CPU(simpy.Resource):
    def __init__(self, quantum_time) -> None:
        super().__init__()

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
    
    def __init__(self) -> None:
        self.tasks = []

    def enqueue(self, task):
        self.tasks.append(task)


def job_creator(_lambda, _mu, priority_weights, priority_queue: Priority_Queue, env: simpy.Environment):
    while True:
        # pending_time = expon.rvs(scale= (1/_lambda), size=1)
        priority = random.choices(([p.value for p in Task.Priority]), weights=priority_weights, k=1)[0]
        pending_time = int(random.expovariate(_lambda))
        yield env.timeout(pending_time)
        arrival_time = env.now
        service_time = int(random.expovariate(1/_mu))
        task = Task(arrival_time, service_time, priority)
        priority_queue.enqueue(task)

# env = simpy.Environment()
# env.process(job_creator(1, 2, [0.7, 0.2, 0.1], Priority_Queue(), env))
# env.run(until = 50)
