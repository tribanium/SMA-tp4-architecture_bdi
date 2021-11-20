import pygame
import numpy as np


class Basecamp(pygame.sprite.Sprite):
    def __init__(self, x, y, size=40):
        super().__init__()
        self.x = x
        self.y = y
        self.pos = np.array([x, y])
        self.size = size
        self.color = (31, 75, 122)
