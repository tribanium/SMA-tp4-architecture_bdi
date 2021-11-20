from simulation import Simulation


if __name__ == "__main__":
    WIDTH = 1000
    HEIGHT = 600

    nb_agents = 20
    nb_rocks = 10

    simu = Simulation(nb_agents, nb_rocks, WIDTH, HEIGHT)
    simu.start()
