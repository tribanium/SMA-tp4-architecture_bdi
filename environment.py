from numpy.core.fromnumeric import size
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

        # initialisation des cailloux
        self.init_rocks_and_base()

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

    def init_rocks_and_base(self):
        min_radius = 5
        max_radius = 20
        factor = 5
        columns = self.width // (factor * max_radius)
        rows = self.height // (factor * max_radius)
        cells = np.array(
            [
                (i * factor * max_radius, j * factor * max_radius)
                for i in range(columns)
                for j in range(rows)
            ]
        )
        areas = cells[np.random.choice(len(cells), replace=False, size=self.nb_rocks)]
        x_base, y_base = areas[0]
        self.base = Basecamp(x_base, y_base)
        for pos in areas[1:]:
            x, y = pos[0], pos[1]
            rock = Rocks(
                self,
                x,
                y,
                color=BLACK_COLOR,
                radius=np.random.randint(min_radius, max_radius),
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
        rxc, ryc = (
            robot_pos[0] + self.robot_size / 2,
            robot_pos[1] + self.robot_size / 2,
        )
        bxc, byc = base_pos[0] + self.base.size / 2, base_pos[1] + self.base.size / 2
        distance = sqrt((bxc - rxc) ** 2 + (byc - ryc) ** 2)
        heading = atan2(byc - ryc, bxc - rxc)
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

    def send_dead_robots_nearby(self, robot):
        robots_nearby = []
        robot_pos = robot.pos
        iterator = (
            r
            for r in self.robots_list
            if ((r.id != robot.id) and (r.battery == 0) and (r.is_helped == False))
        )
        for r in iterator:
            r_pos = r.pos
            distance = sqrt(sum((robot_pos - r_pos) ** 2))
            if distance < robot.vision_field:
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

    def get_nearest_robot(self, robot):
        # Get the dead_robot near the robot
        distance_min = None
        nearest_robot = None
        for r in self.robots_list:
            distance = sqrt(sum((robot.pos - r.pos) ** 2))
            if (not distance_min) or (distance < distance_min):
                distance_min = distance
                nearest_robot = r

        return nearest_robot
