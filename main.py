import pygame
import sys
import numpy as np
import logging

from environment import Environment

# logging.basicConfig(
#     filename="logs.log", filemode="w", encoding="utf-8", level=logging.DEBUG
# )
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (72, 155, 83)

WIDTH = 1000
HEIGHT = 600


class Simulation:
    def __init__(self, width, height, nb_robots=20, nb_rocks=10):
        self.T = 10000
        self.width = width
        self.height = height
        self.robot_size = 10
        self.nb_robots = nb_robots
        self.nb_rocks = nb_rocks
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WIDTH + self.robot_size, HEIGHT + self.robot_size)
        )
        self.env = Environment(
            self, self.nb_robots, self.nb_rocks, self.width, self.height
        )

    def stop_all_threads(self):
        for robot in self.container:
            robot.thread.do_run = False

    def draw_base(self):
        base = self.env.base
        pygame.draw.rect(
            self.screen,
            GREEN_COLOR,
            pygame.Rect(base.x, base.y, base.size, base.size),
        )

    def start(self):

        pygame.display.set_caption("SMA Robots on Mars")
        clock = pygame.time.Clock()

        # conteneur avec tous les robots de la même équipe
        self.container = pygame.sprite.Group()
        self.container_rocks = pygame.sprite.Group()

        # initialisation des robots
        for robot in self.env.robots_list:
            self.container.add(robot)
            robot.thread.start()

        # initialisation des gisements de pierres
        for rock in self.env.rocks_list:
            self.container_rocks.add(rock)

        # Lancement de la simulation pour T itérations
        for i in range(self.T):
            if i % 100 == 0:
                logger.debug(i)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_all_threads()
                    sys.exit()

            self.container_rocks.update()
            self.screen.fill(BACKGROUND_COLOR)

            self.draw_base()
            self.container_rocks.draw(self.screen)
            self.container.draw(self.screen)
            pygame.display.flip()
            clock.tick(30)

        # Stop the thread of each robot
        self.stop_all_threads()

        pygame.quit()


if __name__ == "__main__":
    # Scales up to about 100 agents
    simu = Simulation(WIDTH, HEIGHT, 50, 50)
    simu.start()
