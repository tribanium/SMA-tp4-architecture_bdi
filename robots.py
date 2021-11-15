import pygame
import numpy as np
import threading
import time
import logging

logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)


ACTIONS = ["GO TO THE ROCK", "PICK ROCK"]


class Robot(pygame.sprite.Sprite):
    def __init__(self, env, id, x, y, width, height, velocity=[0, 0]):
        super().__init__()

        self.id = id
        self.size = 10
        self.is_carrying = False
        self.vision_field = 50
        self.communication_field = 100

        self.env = env

        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            self.image, ROBOT_COLOR, pygame.Rect(0, 0, self.size, self.size)
        )
        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.width = width
        self.height = height

        self.thread = threading.Thread(target=self.loop)

    def perception(self):
        return_to_base = self.env.send_return_to_base(self)  # dict
        rocks_nearby = self.env.send_rocks_nearby(self)  # list of dicts
        robots_nearby = self.env.send_robots_nearby(self)  # list of dicts

        return return_to_base, rocks_nearby, robots_nearby

    def option(self):
        epsilon = 5
        return_to_base, rocks_nearby, robots_nearby = self.perception()

        ### Battery

        ### Is there any rock nearby ? If yes, chooses the closest
        heading = None
        option = None
        if rocks_nearby:
            c = 0
            for i, rock in enumerate(rocks_nearby):
                if rock["distance"] < rocks_nearby[c]["distance"]:
                    c = i
            distance = rocks_nearby[c]["distance"]
            heading = rocks_nearby[c]["heading"]
            if distance < epsilon:
                option = "PICK ROCK"
            else:
                option = "GO TO ROCK"

        return option, heading

    # def action(self):
    #     option = self.option()
    #     action = None
    #     return action

    def update(self):
        option, heading = self.option()

        if option == "PICK ROCK":
            self.vel[0], self.vel[1] = 0, 0
        elif option == "GO TO ROCK":
            u = np.asarray([np.cos(heading), np.sin(heading)], dtype=np.float64)
            self.vel = u * np.linalg.norm(self.vel)

        # if rock_pos is not None:
        #     u = rock_pos - self.pos
        #     self.vel = u * np.linalg.norm(self.vel) / np.linalg.norm(u)
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
            time.sleep(0.01)
            self.update()
        logger.debug(f"Thread {self.id} stopped")
