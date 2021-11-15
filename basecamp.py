import pygame
import numpy as np

GREEN_COLOR = (72, 155, 83)


class Basecamp(pygame.sprite.Sprite):
    def __init__(self, x, y, size=40, color=GREEN_COLOR):
        super().__init__()
        self.x = x
        self.y = y
        self.pos = np.array([x, y], dtype=np.float64)
        self.size = size
        self.color = color
