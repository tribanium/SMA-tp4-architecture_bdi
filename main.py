import pygame
import sys
import numpy as np
import time
import threading

from basecamp import Basecamp
from robots import Robot
from rocks import Rocks

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (72, 155, 83)

WIDTH = 1000
HEIGHT = 600


class Simulation:
    def __init__(self, width, height, nb_robots=20, nb_rocks=10):
        self.T = 1000
        self.width = width
        self.height = height
        self.robot_size = 10
        self.nb_robots = nb_robots
        self.nb_rocks = nb_rocks

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WIDTH + self.robot_size, HEIGHT + self.robot_size)
        )
        pygame.display.set_caption("SMA Robots on Mars")

        clock = pygame.time.Clock()

        # conteneur avec tous les robots de la même équipe
        container = pygame.sprite.Group()
        container_rocks = pygame.sprite.Group()

        # quartier général
        base = Basecamp(self.width // 2, self.height // 2)

        # initialisation des robots
        for i in range(self.nb_robots):
            x = (
                base.x
                + 5
                - 2 * base.size
                + (i * 2 * self.robot_size)
                - (i // 10 * 10 * 2 * self.robot_size)
            )
            y = (i // 10) * 2 * self.robot_size + base.y + 50
            vel = np.random.rand(2) * 2 - 1
            robot = Robot(
                x,
                y,
                self.width,
                self.height,
                color=ROBOT_COLOR,
                velocity=vel,
                size=self.robot_size,
            )
            container.add(robot)

        # initialisation des gisements de pierres
        for i in range(self.nb_rocks):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            vel = np.zeros(2)
            rock = Rocks(
                x, y, color=BLACK_COLOR, velocity=vel, radius=np.random.randint(5, 20)
            )
            container_rocks.add(rock)

        # Lancement de la simulation pour T itérations
        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            container.update()
            container_rocks.update()
            self.screen.fill(BACKGROUND_COLOR)

            base.draw(self.screen)
            container_rocks.draw(self.screen)
            container.draw(self.screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    simu = Simulation(WIDTH, HEIGHT)
    simu.nb_robots = 20
    simu.nb_rocks = 10
    simu.start()
