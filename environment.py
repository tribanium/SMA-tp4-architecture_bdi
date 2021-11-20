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

        # rock deposits and base initialization
        self.init_rocks_and_base()

        # hacky formula to initialize robots positions:
        for robot_id in range(self.nb_robots):
            # No one understands this
            x = (
                self.base.x
                + 5
                - 2 * self.base.size
                + (robot_id * 2 * self.robot_size)
                - (robot_id // 10 * 10 * 2 * self.robot_size)
            )
            y = (robot_id // 10) * 2 * self.robot_size + self.base.y + 50

            robot = Robot(self, robot_id, x, y, self.width, self.height)
            self.robots_list.append(robot)

    def init_rocks_and_base(self):
        """Initializes rocks and bases. The screen is divided in cells and a 
        random number of cells is selected to contain rocks"""
        min_radius = 5
        max_radius = 20
        factor = 5
        columns = self.width // (factor * max_radius)
        rows = self.height // (factor * max_radius)
        cells = np.array(
            [
                (col * factor * max_radius, row * factor * max_radius)
                for col in range(columns)
                for row in range(rows)
            ]
        )
        areas = cells[np.random.choice(
            len(cells), replace=False, size=self.nb_rocks)]
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
                heading = atan2(rock_pos[1] - robot_pos[1],
                                rock_pos[0] - robot_pos[0])
                rocks_nearby.append({"distance": distance, "heading": heading})
        return rocks_nearby

    def send_base_data(self, robot):
        base_pos = self.base.pos
        robot_pos = robot.pos

        # Position of the center of the robot
        rxc = robot_pos[0] + self.robot_size / 2
        ryc = robot_pos[1] + self.robot_size / 2,

        # Position of the center of the base
        bxc = base_pos[0] + self.base.size / 2
        byc = base_pos[1] + self.base.size / 2

        # Distance and heading calculations
        distance = sqrt((bxc - rxc) ** 2 + (byc - ryc) ** 2)
        heading = atan2(byc - ryc, bxc - rxc)
        base_data_dict = {"distance": distance, "heading": heading}
        return base_data_dict

    def send_dead_robots_nearby(self, robot):
        dead_robots_nearby = []
        iterator = (r for r in self.robots_list
                    if ((r.id != robot.id) and (r.battery == 0) and (r.is_helped == False))
                    )
        for r in iterator:
            distance = sqrt(sum((robot.pos - r.pos) ** 2))
            if distance < robot.vision_field:
                heading = atan2(r.pos[1] - robot.pos[1],
                                r.pos[0] - robot.pos[0])
                dead_robots_nearby.append(
                    {"distance": distance, "heading": heading})
        return dead_robots_nearby

    def send_message_to_robots_nearby(self, robot, message):
        iterator = (r for r in self.robots_list if (
            r.id != robot.id and r.battery > 0))

        for other_robot in iterator:
            distance = sqrt(sum((other_robot.pos - robot.pos) ** 2))
            if distance < robot.communication_field:
                heading = atan2(
                    other_robot.pos[1] -
                    robot.pos[1], other_robot.pos[0] - robot.pos[0]
                )
                to_send = {"header": (distance, heading), "message": message}
                other_robot.messages.put(to_send)

    def delete_rocks(self, rock):
        self.simu.rocks_container.remove(rock)
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

            if distance < distance_min:
                distance_min = distance
                nearest_rock = rock

        return nearest_rock

    def get_nearest_robot(self, robot):
        # Get the dead_robot near the robot
        distance_min = None
        nearest_robot = None
        for r in self.robots_list:
            if r.battery == 0:
                distance = sqrt(sum((robot.pos - r.pos) ** 2))

                if not distance_min:
                    distance_min = distance
                    nearest_robot = r

                if distance < distance_min:
                    distance_min = distance
                    nearest_robot = r

        if nearest_robot is None:
            return Exception("No nearest robot without battery")

        return nearest_robot
