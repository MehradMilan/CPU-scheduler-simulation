import simulation as sim
def main():
    X, Y, Z = [float(x) for x in input().split()]
    job_count = int(input())
    simulation_time = int(input())
    sim.run_simulation(X, Y, Z, job_count, simulation_time)

if __name__ == "__main__":
    main()

