import simpy
import random
from scipy.stats import expon

class CPU(simpy.Resource):
    def __init__(self, quantum_time) -> None:
        super().__init__()


class Task:
    pid = 0

    def __init__(self, arrival_time, service_time) -> None:
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.pid = Task.pid
        Task.pid += 1

class Priority_Queue:
    
    def __init__(self) -> None:
        self.tasks = []

    def enqueue(self, task):
        self.tasks.append(task)


def job_creator(env: simpy.Environment, _lambda, _mu, priority_queue: Priority_Queue):
    while True:
        # pending_time = expon.rvs(scale= (1/_lambda), size=1)
        pending_time = int(random.expovariate(_lambda))
        yield env.timeout(pending_time)
        arrival_time = env.now
        service_time = int(random.expovariate(1/_mu))
        task = Task(arrival_time, service_time)
        priority_queue.enqueue(task)

# env = simpy.Environment()
# env.process(job_creator(env, 1, 2))
# env.run(until = 50)
