from robots import Robot, MAX_VEL_NORM
from basecamp import Basecamp
from rocks import Rocks
import logging

from math import atan2, sqrt
import numpy as np

ROBOT_COLOR = (250, 120, 60)
BLACK_COLOR = (0, 0, 0)

logger = logging.getLogger(__name__)


class Environment:
    def __init__(self, simu, nb_robots, nb_rocks, width, height):
        self.simu = simu
        self.nb_robots = nb_robots
        self.nb_rocks = nb_rocks
        self.width = width
        self.height = height
        self.robot_size = 10

        self.robots_list = []
        self.rocks_list = []
        self.base = Basecamp(self.width // 2, self.height // 2)

        # initialisation des robots:
        for i in range(self.nb_robots):
            x = (
                self.base.x
                + 5
                - 2 * self.base.size
                + (i * 2 * self.robot_size)
                - (i // 10 * 10 * 2 * self.robot_size)
            )
            y = (i // 10) * 2 * self.robot_size + self.base.y + 50
            robot = Robot(self, i, x, y, self.width, self.height)
            self.robots_list.append(robot)

        # initialisation des cailloux
        for i in range(self.nb_rocks):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            # x, y = 100, 100
            vel = np.zeros(2)
            rock = Rocks(
                self,
                x,
                y,
                color=BLACK_COLOR,
                radius=np.random.randint(5, 20),
            )
            self.rocks_list.append(rock)

    def send_rocks_nearby(self, robot):
        rocks_nearby = []
        robot_pos = robot.pos
        for rock in self.rocks_list:
            rock_pos = rock.pos + rock.radius - robot.size / 2
            distance = sqrt(sum((robot_pos - rock_pos) ** 2))
            if distance < robot.vision_field:
                heading = atan2(rock_pos[1] - robot_pos[1], rock_pos[0] - robot_pos[0])
                rocks_nearby.append({"distance": distance, "heading": heading})
        return rocks_nearby

    def send_return_to_base(self, robot):
        base_pos = self.base.pos
        robot_pos = robot.pos
        distance = sqrt(sum((robot_pos - base_pos) ** 2))
        heading = atan2(base_pos[1] - robot_pos[1], base_pos[0] - robot_pos[0])
        return_to_base_dict = {"distance": distance, "heading": heading}
        return return_to_base_dict

    def send_robots_nearby(self, robot):
        robots_nearby = []
        robot_pos = robot.pos
        iterator = (r for r in self.robots_list if r.id != robot.id)
        for r in iterator:
            r_pos = r.pos
            distance = sqrt(sum((robot_pos - r_pos) ** 2))
            if distance < robot.communication_field:
                heading = atan2(r_pos[1] - robot_pos[1], r_pos[0] - robot_pos[0])
                robots_nearby.append({"distance": distance, "heading": heading})
        return robots_nearby

    def delete_rocks(self, rock):
        self.simu.container_rocks.remove(rock)
        self.rocks_list.remove(rock)

    def get_nearest_rock(self, robot):
        # Get the rock near the robot
        distance_min = None
        nearest_rock = None
        for rock in self.rocks_list:
            distance = sqrt(sum((robot.pos - rock.pos) ** 2))
            if not distance_min:
                distance_min = distance
                nearest_rock = rock
            elif distance < distance_min:
                distance_min = distance
                nearest_rock = rock

        return nearest_rock
