import pygame
import numpy as np


BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)


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
