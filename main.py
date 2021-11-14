import pygame
import sys
import numpy as np
import time

# BACKGROUND_COLOR = (12, 24, 36)
BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (0, 255, 0)

WIDTH = 1000
HEIGHT = 600


class Robot(pygame.sprite.Sprite):
    def __init__(
        self, x, y, width, height, color=ROBOT_COLOR, size=10, velocity=[0, 0]
    ):
        super().__init__()
        self.image = pygame.Surface([size, size])
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, size, size))

        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.width = width
        self.height = height

    def update(self):
        self.pos += self.vel
        x, y = self.pos

        # Conditions limites
        if (x < 0) or (x > self.width):
            self.vel[0] = -self.vel[0]

        if (y < 0) or (y > self.height):
            self.vel[1] = -self.vel[1]

        # Update de la position du rectangle
        self.rect.x = x
        self.rect.y = y


class Basecamp(pygame.sprite.Sprite):
    def __init__(self, x, y, size=40, color=GREEN_COLOR):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size)
        )


class Rocks(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, radius=5):
        super().__init__()
        self.x = x
        self.y = y
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.image = pygame.Surface((radius * 2, radius * 2))
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()

    def update(self):
        self.pos += self.vel
        x, y = self.pos

        self.rect.x = x
        self.rect.y = y


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
            vel = np.random.rand(2) * 4 - 2
            # vel = np.zeros(2)
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

        for i in range(self.nb_rocks):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            vel = np.zeros(2)
            rock = Rocks(x, y, color=BLACK_COLOR, velocity=vel)
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
            container.draw(self.screen)
            container_rocks.draw(self.screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    simu = Simulation(WIDTH, HEIGHT)
    simu.nb_robots = 20
    simu.nb_rocks = 10
    simu.start()
