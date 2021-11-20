import pygame
import numpy as np
import threading
import time
import logging
from colour import Color
from math import sqrt, atan2

logger = logging.getLogger(__name__)

red = Color("red")
robot_colors = list(red.range_to(Color("green"), 101))

BACKGROUND_COLOR = (234, 213, 178)
ROBOT_COLOR = (250, 120, 60)
ROBOT_COLOR_CARRY = (0, 0, 255)
BLACK_COLOR = (0, 0, 0)


MAX_VEL_NORM = 1.5


class Robot(pygame.sprite.Sprite):
    def __init__(self, env, id, x, y, width, height):
        super().__init__()

        self.id = id
        self.size = 10
        self.is_carrying = False
        self.vision_field = 50
        self.communication_field = 100
        self.state = None
        self.battery = 100
        self.need_charge = False
        self.t = 0
        self.is_helped = False

        self.env = env

        self.color = ROBOT_COLOR
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            self.image, self.color, pygame.Rect(0, 0, self.size, self.size)
        )
        self.rect = self.image.get_rect()

        self.pos = np.array([x, y], dtype=np.float64)
        norm = MAX_VEL_NORM * np.random.uniform(0.3, 1)
        heading = np.random.uniform(0, 2 * np.pi)
        self.vel = norm * np.array([np.cos(heading), np.sin(heading)])

        self.width = width
        self.height = height

        self.thread = threading.Thread(target=self.loop)
        self.lock = threading.Lock()

    def mine_rock(self, rock):
        self.lock.acquire()
        if rock is not None:
            rock.radius -= 1.5
            self.is_carrying = True
        self.lock.release()

    def help_robot(self, dead_robot):
        dead_robot.is_helped = True
        dead_robot.battery = self.battery // 2
        self.battery = self.battery // 2
        dead_robot.is_helped = False

    def release_rock(self):
        self.is_carrying = False
        self.color = ROBOT_COLOR

    def perception(self):
        return_to_base = self.env.send_return_to_base(self)  # dict
        rocks_nearby = self.env.send_rocks_nearby(self)  # list of dicts
        robots_nearby = self.env.send_robots_nearby(self)  # list of dicts
        dead_robots = self.env.send_dead_robots_nearby(self)

        return return_to_base, rocks_nearby, robots_nearby, dead_robots

    def option(self):
        epsilon = MAX_VEL_NORM / 2
        (
            return_to_base,
            rocks_nearby,
            robots_discharged_nearby,
            dead_robots,
        ) = self.perception()

        ### Battery
        if self.battery == 0:
            option = "NO BATTERY"
            heading = None
            return option, heading

        ### Return to base
        elif (self.is_carrying) or (self.battery < 10):
            if self.is_carrying:
                self.carry_rock()
            if self.battery < 10:
                self.need_charge = True
            option = "RETURN TO BASE"
            heading = return_to_base["heading"]
            distance_to_base = return_to_base["distance"]
            if distance_to_base < epsilon:
                option = "CHARGE"
                if self.is_carrying:
                    option = "DROP TO BASE"
                heading = None

        elif dead_robots and (self.battery > 30):
            heading = None
            option = None
            dead_robots_distances = [robot["distance"] for robot in dead_robots]
            nearest_dead_robot = np.argmin(dead_robots_distances)
            distance = dead_robots[nearest_dead_robot]["distance"]
            heading = dead_robots[nearest_dead_robot]["heading"]
            if distance < self.size:
                option = "HELP ROBOT"
            else:
                option = "GO TO ROBOT"

        ### Is there any rock nearby ? If yes, chooses the closest
        elif rocks_nearby:
            heading = None
            option = None
            rocks_distances = [rock["distance"] for rock in rocks_nearby]
            nearest_rock_index = np.argmin(rocks_distances)
            distance = rocks_nearby[nearest_rock_index]["distance"]
            heading = rocks_nearby[nearest_rock_index]["heading"]
            if distance < epsilon:
                option = "PICK ROCK"
            else:
                option = "GO TO ROCK"

        else:
            option, heading = "SEARCH ROCK", None

        return option, heading

    def update(self):
        self.battery_color()
        self.t += 1
        if (self.t % 10 == 0) and (self.battery > 0) and (np.random.rand() > 0.7):
            self.battery -= 1

        option, heading = self.option()

        if option == "NO BATTERY":
            self.vel[0], self.vel[1] = 0, 0
            self.dead_robot()

        elif option == "RETURN TO BASE":
            u = np.array([np.cos(heading), np.sin(heading)])
            self.vel = u * MAX_VEL_NORM

        elif option == "CHARGE":
            self.vel[0], self.vel[1] = 0, 0
            self.battery = 100
            self.need_charge = False
            # time.sleep(5)

        elif option == "GO TO ROBOT":
            new_vel = np.array([np.cos(heading), np.sin(heading)])
            self.vel = new_vel * MAX_VEL_NORM

        elif option == "HELP ROBOT":
            self.vel[0], self.vel[1] = 0, 0
            dead_robot = self.env.get_nearest_robot(self)
            self.help_robot(dead_robot)

        elif option == "DROP TO BASE":
            self.vel[0], self.vel[1] = 0, 0
            self.release_rock()
            # time.sleep(1)

        elif option == "SEARCH ROCK":
            if not self.vel.any():
                norm = MAX_VEL_NORM * np.random.uniform(0.3, 1)
                heading = np.random.uniform(0, 2 * np.pi)
                self.vel = norm * np.array([np.cos(heading), np.sin(heading)])
            elif self.t % 100 == 0:
                # Adding random movement every 100 iteration
                heading = atan2(self.vel[1], self.vel[0]) + np.random.uniform(
                    -np.pi / 3, np.pi / 3
                )
                self.vel = np.linalg.norm(self.vel) * np.array(
                    [np.cos(heading), np.sin(heading)]
                )

        elif option == "GO TO ROCK":
            # Change vel orientation
            new_vel = np.array([np.cos(heading), np.sin(heading)])
            self.vel = new_vel * MAX_VEL_NORM

        elif option == "PICK ROCK":
            self.vel[0], self.vel[1] = 0, 0
            rock = self.env.get_nearest_rock(self)
            self.mine_rock(rock)
            # time.sleep(1)

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

    # def change_color(self):
    #     # pygame.draw.rect(
    #     #     self.image, self.color, pygame.Rect(0, 0, self.size, self.size)
    #     # )
    #     pass

    def carry_rock(self):
        color = robot_colors[int(self.battery)]
        color_rgb = tuple([int(255 * x) for x in color.rgb])
        pygame.draw.circle(
            self.image, BLACK_COLOR, [self.size // 2, self.size // 2], self.size // 4
        )

    def battery_color(self):
        color = robot_colors[int(self.battery)]
        color_rgb = tuple([int(255 * x) for x in color.rgb])
        pygame.draw.rect(self.image, color_rgb, pygame.Rect(0, 0, self.size, self.size))

    def dead_robot(self):
        pygame.draw.line(self.image, BLACK_COLOR, (0, 0), (self.size, self.size))
        pygame.draw.line(self.image, BLACK_COLOR, (self.size, 0), (0, self.size))

    def loop(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            time.sleep(0.01)
            self.update()
        logger.debug(f"Thread {self.id} stopped")
