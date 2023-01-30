import simpy
import random
from scheduler.queue import Priority_Queue, Waiting_Queue, Task

class CPU(simpy.Resource):
    def __init__(self, waiting_queue, queue_list, env) -> None:
        super().__init__(env)
        self.waiting_queue = waiting_queue
        self.queue_list = queue_list
        self.idle_time = 0



def job_creator(_lambda, _mu, Z, priority_weights, cp, waiting_queue: Priority_Queue, env: simpy.Environment):
    i = 0
    while i < cp:
        priority = random.choices(([p.value for p in Task.Priority]), weights=priority_weights, k=1)[0]
        pending_time = int(random.expovariate(_lambda))
        yield env.timeout(pending_time)
        arrival_time = env.now
        service_time = int(random.expovariate(1/_mu))
        max_timeout = int(random.expovariate(1/Z))
        task = Task(arrival_time, service_time, max_timeout, priority)
        task.update_queue_enter_time(waiting_queue.name, env.now)
        task.ss = env.process(task.start_starving(env))
        waiting_queue.enqueue(task)
        print(str(env.now) + " " + "Task {} created".format(task.pid) + " Priority: " + str(task.priority) + " Arrival Time: " + str(task.arrival_time) + " Service Time: " + str(task.service_time) + " Max Timeout: " + str(task.max_timeout))
        i += 1

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
        yield env.timeout(1)
        with cpu.request() as req:
            yield req
            queue = choose_queue(cpu.queue_list, queue_choose_weights)
            if queue:
                print(str(env.now) + " " + "Dispatcher choose queue: " + queue.name)
                task = None
                while not task:
                    task = queue.dequeue()
                    if task.ss:
                        task.ss.interrupt()
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
                cpu.idle_time += 1
                print(str(env.now) + " " + "CPU is idle")
