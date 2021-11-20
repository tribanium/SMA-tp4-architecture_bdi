
from simulation import Simulation, WIDTH, HEIGHT

# logging.basicConfig(
#     filename="logs.log", filemode="w", encoding="utf-8", level=logging.DEBUG
# )


if __name__ == "__main__":
    # Scales up to about 100 agents

    nb_agents = 20
    nb_rocks = 10

    simu = Simulation(nb_agents, nb_rocks, WIDTH, HEIGHT)
    simu.start()
