import pygame
import numpy as np
import threading
import time
import logging
from math import sqrt

logger = logging.getLogger(__name__)

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)
ROBOT_COLOR_CARRY = (0, 0, 255)


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

        self.color = ROBOT_COLOR
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            self.image, self.color, pygame.Rect(0, 0, self.size, self.size)
        )
        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.width = width
        self.height = height

        self.thread = threading.Thread(target=self.loop)
        self.lock = threading.Lock()

    def mine_rock(self, rock):
        self.lock.acquire()
        if rock is not None:
            rock.radius -= 1
            self.is_carrying = True
            self.color = ROBOT_COLOR_CARRY
        self.lock.release()

    def release_rock(self):
        self.is_carrying = False
        self.color = ROBOT_COLOR

    def perception(self):
        return_to_base = self.env.send_return_to_base(self)  # dict
        rocks_nearby = self.env.send_rocks_nearby(self)  # list of dicts
        robots_nearby = self.env.send_robots_nearby(self)  # list of dicts

        return return_to_base, rocks_nearby, robots_nearby

    def option(self):
        epsilon = sqrt(2) / 2
        return_to_base, rocks_nearby, robots_nearby = self.perception()

        ### Battery

        ### Return to base
        if self.is_carrying:
            option = "RETURN TO BASE"
            heading = return_to_base["heading"]
            distance_to_base = return_to_base["distance"]
            if distance_to_base < epsilon:
                option = "DROP TO BASE"
                heading = None

            # option, heading = (
            #     ("DROP TO BASE", None)
            #     if return_to_base["distance"] < epsilon
            #     else ("RETURN TO BASE", return_to_base["heading"])
            # )

        ### Is there any rock nearby ? If yes, chooses the closest
        elif rocks_nearby:
            heading = None
            option = None
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

        else:
            option, heading = "SEARCH ROCK", None

        return option, heading

    # def action(self):
    #     option = self.option()
    #     action = None
    #     return action

    def update(self):
        option, heading = self.option()

        if option == "RETURN TO BASE":
            u = np.asarray([np.cos(heading), np.sin(heading)], dtype=np.float64)
            self.vel = u * sqrt(2)

        elif option == "DROP TO BASE":
            self.vel[0], self.vel[1] = 0, 0
            self.release_rock()
            time.sleep(1)

        elif option == "SEARCH ROCK":
            if not self.vel.any():
                self.vel = np.random.rand(2) * 2 - 1

        elif option == "GO TO ROCK":
            # Change vel orientation
            u = np.asarray([np.cos(heading), np.sin(heading)], dtype=np.float64)
            self.vel = u * sqrt(2)

        elif option == "PICK ROCK":
            self.vel[0], self.vel[1] = 0, 0
            rock = self.env.get_nearest_rock(self)
            self.mine_rock(rock)
            time.sleep(1)

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

        self.change_color()

    def change_color(self):
        pygame.draw.rect(
            self.image, self.color, pygame.Rect(0, 0, self.size, self.size)
        )

    def loop(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            time.sleep(0.01)
            self.update()
        logger.debug(f"Thread {self.id} stopped")
