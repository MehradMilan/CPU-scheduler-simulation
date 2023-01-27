from scheduler import priority_queue
import cpu_env
import simpy

env = simpy.Environment()
cpu = cpu_env.CPU(cpu_env.Waiting_Queue("Waiting_Queue", 1, 0.01), [cpu_env.Priority_Queue("Round_Robin_T1", 5, 0), cpu_env.Priority_Queue("Round_Robin_T2", 10, 1), cpu_env.Priority_Queue("FCFS", None, 2)], env)
env.process(cpu_env.job_creator(0.3, 5, 10, [0.7, 0.2, 0.1], 30, cpu.waiting_queue, env))
env.process(cpu_env.job_loader(5, 5, cpu.waiting_queue, cpu.queue_list, env))
env.process(cpu_env.dispatcher([0.8, 0.1, 0.1], cpu, env))
env.run(until = 50)
for t in cpu_env.Task.all_tasks:
    print(str(t))
print(cpu.idle_time)