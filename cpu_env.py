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

    def enqueue(self, task):
        self.tasks.append(task)

    def dequeue(self) -> Task:
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

def job_creator(_lambda, _mu, Z, priority_weights, waiting_queue: Priority_Queue, env: simpy.Environment):
    while True:
        priority = random.choices(([p.value for p in Task.Priority]), weights=priority_weights, k=1)[0]
        pending_time = int(random.expovariate(_lambda))
        yield env.timeout(pending_time)
        arrival_time = env.now
        service_time = int(random.expovariate(1/_mu))
        max_timeout = int(random.expovariate(1/Z))
        task = Task(arrival_time, service_time, max_timeout, priority)
        task.update_queue_enter_time(waiting_queue.name, env.now)
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
                    task.update_queue_exit_time(waiting_queue.name, env.now)
                    queue_list[0].enqueue(task)
                    task.update_queue_enter_time(queue_list[0].priority.name, env.now)
            print(str(env.now) + " " + "Job loading..." + " " + "Waiting Queue: " + str(waiting_queue.length()))
            for q in queue_list:
                print(q.name + ": " + str(q.length()))
        yield env.timeout(sleep_time)

def choose_queue(queue_list, weights) -> Priority_Queue:
    q = random.choices(queue_list, weights=weights, k=1)[0]
    if q.length() > 0:
        return q
    else:
        return None

    # for q in queue_list:
    #     if q.length() > 0:
    #         return q
    #     return None

def dispatcher(queue_choose_weights, cpu: CPU, env: simpy.Environment):
    while True:
        with cpu.request() as req:
            yield req
            queue = choose_queue(cpu.queue_list, queue_choose_weights)
            if queue:
                print(str(env.now) + " " + "Dispatcher choose queue: " + queue.name)
                task = queue.dequeue()
                task.update_queue_exit_time(queue.priority.name, env.now)
                print(str(env.now) + " " + "Task {} started".format(task.pid))
                if queue.Q_time:
                    spend_time = min(task.remaining_time, queue.Q_time)
                    yield env.timeout(spend_time)
                    task.remaining_time -= spend_time
                    if task.remaining_time > 0:
                        cpu.queue_list[queue.priority.value + 1].enqueue(task)
                        task.update_queue_enter_time(cpu.queue_list[queue.priority.value + 1].priority.name, env.now)
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
