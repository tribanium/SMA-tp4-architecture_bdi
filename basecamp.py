import pygame
import numpy as np

GREEN_COLOR = (72, 155, 83)


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
