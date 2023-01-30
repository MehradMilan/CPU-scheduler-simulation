from scheduler.cpu_env import *
from scheduler.queue import Priority_Queue, Waiting_Queue

TASKS_PROBS = [0.7, 0.2, 0.1]
QUEUE_PROBS = [0.8, 0.1, 0.1]
K_LOAD = 5
LOAD_INTERARRIVAL = 5
Round_Robin_T1_QUANTUM_TIME = 2
Round_Robin_T2_QUANTUM_TIME = 4
WAITING_QUEUE_P_COEFF = 1
WAITING_QUEUE_T_COEFF = 0.01

def run_simulation(X, Y, Z, job_count, simulation_time):
    print("X: " + str(X) + " Y: " + str(Y) + " Z: " + str(Z))
    env = simpy.Environment()
    cpu = CPU(Waiting_Queue("Waiting_Queue", WAITING_QUEUE_P_COEFF, WAITING_QUEUE_T_COEFF),
    [Priority_Queue("Round_Robin_T1", Round_Robin_T1_QUANTUM_TIME, 0), Priority_Queue("Round_Robin_T2", Round_Robin_T2_QUANTUM_TIME, 1), Priority_Queue("FCFS", None, 2)], env)
    env.process(job_creator(X, Y, Z, TASKS_PROBS, job_count, cpu.waiting_queue, env))
    env.process(job_loader(LOAD_INTERARRIVAL, K_LOAD, cpu.waiting_queue, cpu.queue_list, env))
    env.process(dispatcher(QUEUE_PROBS, cpu, env))
    env.run(until = simulation_time)
    for t in Task.all_tasks:
        if not t.is_timeout:
            t.update_queue_exit_time(t.current_queue.name, simulation_time)
        print(str(t))
    print('Waiting queue mean length:')
    print(queue_length_mean(cpu.waiting_queue, simulation_time))
    for q in cpu.queue_list:
        print(q.name + ' mean length:')
        print(queue_length_mean(q, simulation_time))

    print('Waiting queue mean time spent in queue:')
    print(time_spent_in_queue(cpu.waiting_queue, Task.all_tasks))
    for q in cpu.queue_list:
        print(q.name + ' mean time spent in queue:')
        print(time_spent_in_queue(q, Task.all_tasks))

    print('CPU idle time:')
    print(cpu.idle_time)

    print('CPU utilization:')
    print(cpu_utilization(cpu, simulation_time))

    print('Timeout task percent:')
    print(timeout_task_percent(Task.all_tasks))


def queue_length_mean(queue, simulation_time):
    qlm = 0
    for t in Task.all_tasks:
        tq = t.spend_times[queue.name][1] - t.spend_times[queue.name][0]
        if tq > 0:
            qlm += tq
    return qlm / simulation_time

def time_spent_in_queue(queue, task):
    tsiq = 0
    for t in Task.all_tasks:
        tq = t.spend_times[queue.name][1] - t.spend_times[queue.name][0]
        if tq > 0:
            tsiq += tq
    return tsiq / len(Task.all_tasks)

def cpu_utilization(cpu, simulation_time):
    return (simulation_time - cpu.idle_time) / simulation_time

def timeout_task_percent(tasks):
    return len([t for t in tasks if t.is_timeout]) / len(tasks)