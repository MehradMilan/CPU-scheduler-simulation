import simpy
import random
import enum

class CPU(simpy.Resource):
    def __init__(self, waiting_queue, queue_list, env) -> None:
        super().__init__(env)
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
        self.remaining_time = self.service_time
        self.arrival_time = arrival_time
        self.is_finished = False
        self.is_timeout = False
        self.pid = Task.pid
        Task.pid += 1

class Priority_Queue:

    class Priority(enum.Enum):
        RR_T1 = 0
        RR_T2 = 1
        FCFS = 2
    
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
        print(str(env.now) + " " + "Task {} created".format(task.pid) + " Priority: " + str(task.priority) + " Arrival Time: " + str(task.arrival_time) + " Service Time: " + str(task.service_time))

def job_loader(sleep_time, K, waiting_queue: Waiting_Queue, queue_list, env: simpy.Environment):
    while True:
        t = 0
        for q in queue_list:
            t += q.length()
        if t < K:
            waiting_queue.sort_tasks()
            new_tasks = waiting_queue.dequeue(K)
            if new_tasks:
                for task in new_tasks:
                    queue_list[0].enqueue(task)
            print(str(env.now) + " " + "Job loading..." + " " + "Waiting Queue: " + str(waiting_queue.length()))
            for q in queue_list:
                print(q.name + ": " + str(q.length()))
        yield env.timeout(sleep_time)

def choose_queue(queue_list):
    for q in queue_list:
        if q.length() > 0:
            return q
        return None

def dispatcher(env, cpu: CPU):
    while True:
        with cpu.request() as req:
            yield req
            queue = choose_queue(cpu.queue_list)
            if queue:
                task = queue.dequeue()
                print(str(env.now) + " " + "Task {} started".format(task.pid))
                if queue.Q_time:
                    spend_time = min(task.remaining_time, queue.Q_time)
                    yield env.timeout(spend_time)
                    task.remaining_time -= spend_time
                    if task.remaining_time > 0:
                        print(str(env.now) + " " + queue.name)
                        print(len(cpu.queue_list))
                        print(queue.priority.value)
                        cpu.queue_list[queue.priority.value + 1].enqueue(task)
                    else:
                        task.is_finished = True
                        print(str(env.now) + " " + "Task {} finished".format(task.pid))
                else:
                    yield env.timeout(task.remaining_time)
                    task.remaining_time = 0
                    task.is_finished = True
                    print(str(env.now) + " " + "Task {} finished".format(task.pid))
            else:
                print(str(env.now) + " " + "CPU is idle")   
        yield env.timeout(1) 
    # env = simpy.Environment()
    # env.process(job_creator(1, 2, [0.7, 0.2, 0.1], Priority_Queue(), env))
    # env.run(until = 50)
