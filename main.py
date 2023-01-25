from scheduler import priority_queue
import cpu_env
import simpy

cpu = cpu_env.CPU(cpu_env.Waiting_Queue("Priority_Queue", 1, 0.01), [cpu_env.Priority_Queue("Round_Robin_T1", 5, 2), cpu_env.Priority_Queue("Round_Robin_T2", 10, 1), cpu_env.Priority_Queue("FCFS", None, 0)])
env = simpy.Environment()
env.process(cpu_env.job_creator(1, 2, [0.7, 0.2, 0.1], cpu.waiting_queue, env))
env.process(cpu_env.job_loader(10, 5, cpu.waiting_queue, cpu.queue_list, env))
env.run(until = 50)