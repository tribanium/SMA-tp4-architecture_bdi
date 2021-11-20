################################################
# MULTI AGENTS SYSTEMS - MINING ROBOTS ON MARS #
################################################
"""
Authors : Nathan ETOURNEAU, Paul FLAGEL.

This project based on pygame aims at implementing a multi-agent system made of 
robots designed under a Belief-Desire-Intention (BDI) architecture.

The robots come from a base and have to explore the planet to mine stone deposits. 
They don't know their absolute coordinates, and move in a random direction until a deposit appears in their field of vision, 
or a nearby neighbor informs them that a deposit is nearby. Once the robot has retrieved its stones, 
it returns directly to its base from which it always knows the direction, to deposit their stones and then start looking for deposits again. 
The deposits decrease as they are mined by the robots and the simulation ends when no more deposits are available.

In order for each robot to carry out its objectives independently of the others, the simulation is multithreaded 
i.e. each agent evolves in its own thread, and works regardless of the actions performed by the other agents.
"""
from simulation import Simulation

# To get started, choose the number of robots you want.
# You can optionally change the number of rocks and the WIDTH and HEIGHT to adapt it to your screen.

if __name__ == "__main__":
    WIDTH = 1000
    HEIGHT = 600

    nb_agents = 20
    nb_rocks = 10

    simu = Simulation(nb_agents, nb_rocks, WIDTH, HEIGHT)
    simu.start()
