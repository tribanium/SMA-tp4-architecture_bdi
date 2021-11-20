import pygame
import numpy as np

BACKGROUND_COLOR = (234, 213, 178)


class Rocks(pygame.sprite.Sprite):
    def __init__(self, env, x, y, color, radius=5):
        super().__init__()
        self.x = x
        self.y = y
        self.env = env
        self.radius = radius
        self.color = color
        self.pos = np.array([x, y], dtype=np.float64)

        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        pygame.draw.circle(self.image, color,
                           (self.radius, self.radius), self.radius)
        self.image.fill(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos

    def update(self):
        # Test if a rock is completely mined
        if self.radius > 0:
            self.image = pygame.Surface((self.radius * 2, self.radius * 2))
            self.image.fill(BACKGROUND_COLOR)
            pygame.draw.circle(
                self.image, self.color, (self.radius, self.radius), self.radius
            )
        else:
            self.env.delete_rocks(self)
