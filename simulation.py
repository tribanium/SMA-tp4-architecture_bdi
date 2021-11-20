import pygame
import sys
import logging
import time

from environment import Environment

BACKGROUND_COLOR = (234, 213, 178)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Simulation:
    def __init__(self, nb_robots=20, nb_rocks=10, width=1000, height=600):
        self.T = 5000
        self.width = width
        self.height = height
        self.robot_size = 10
        self.nb_robots = nb_robots
        self.nb_rocks = nb_rocks
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width + self.robot_size, self.height + self.robot_size)
        )
        self.env = Environment(
            self, self.nb_robots, self.nb_rocks, self.width, self.height
        )

    def stop_all_threads(self):
        """Interrupts all the threads in which the robots are running."""
        for robot in self.robots_container:
            robot.thread.do_run = False

    def draw_base(self):
        """Draws the base on the screen"""
        base = self.env.base
        pygame.draw.rect(
            self.screen,
            self.env.base.color,
            pygame.Rect(base.x, base.y, base.size, base.size),
        )

    def start(self):
        """Runs the simulation of the robots on mars"""
        pygame.display.set_caption("SMA Robots on Mars")
        clock = pygame.time.Clock()

        # Container with all the robots
        self.robots_container = pygame.sprite.Group()
        self.rocks_container = pygame.sprite.Group()

        # rocks deposits initialisation
        for rock in self.env.rocks_list:
            self.rocks_container.add(rock)

        self.rocks_container.update()

        # Background with a mars-like color
        self.screen.fill(BACKGROUND_COLOR)

        # We draw the base and the rocks
        self.draw_base()
        self.rocks_container.draw(self.screen)
        pygame.display.flip()
        time.sleep(2)

        # We initialize the robots and launch their loop in their own private thread
        for robot in self.env.robots_list:
            self.robots_container.add(robot)
            robot.thread.start()

        # Launch the simulation for T iterations
        for i in range(self.T):

            # Log message every 100 iterations
            if i % 100 == 0:
                logger.debug(i)

            # If one quits, loop interruption
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_all_threads()
                    sys.exit()

            # We draw over the rocks, the robots, the base and the background
            self.rocks_container.update()
            self.screen.fill(BACKGROUND_COLOR)

            self.draw_base()
            self.rocks_container.draw(self.screen)
            self.robots_container.draw(self.screen)
            pygame.display.flip()
            clock.tick(30)

        # Stop the thread of each robot
        self.stop_all_threads()

        pygame.quit()
