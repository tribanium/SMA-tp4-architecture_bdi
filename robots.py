import pygame
import numpy as np
import threading
import time
import logging

logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)


class Robot(pygame.sprite.Sprite):
    def __init__(
        self, id, x, y, width, height, color=ROBOT_COLOR, size=10, velocity=[0, 0]
    ):
        super().__init__()
        self.id = id
        self.image = pygame.Surface([size, size])
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, size, size))

        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.width = width
        self.height = height

        self.thread = threading.Thread(target=self.loop)

    def update(self, rock_pos=None):
        if rock_pos is not None:
            u = rock_pos - self.pos
            self.vel = u * np.linalg.norm(self.vel) / np.linalg.norm(u)
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

    def loop(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            time.sleep(0.025)
            self.update()
        logger.debug(f"Thread {self.id} stopped")
