import pygame
import numpy as np

BACKGROUND_COLOR = (234, 213, 178)


class Rocks(pygame.sprite.Sprite):
    def __init__(self, env, x, y, color, velocity, radius=5):
        super().__init__()
        self.x = x
        self.y = y
        self.env = env
        self.radius = radius
        self.color = color
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

    def update(self):
        self.pos += self.vel
        x, y = self.pos

        self.rect.x = x
        self.rect.y = y

        # self.radius -= 0.05

        # if self.radius > 0:
        #     self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        #     self.image.fill(BACKGROUND_COLOR)
        #     pygame.draw.circle(
        #         self.image, self.color, (self.radius, self.radius), self.radius
        #     )
        # else:
        #     self.env.delete_rocks(self)
