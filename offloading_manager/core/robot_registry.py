from offloading_manager.routers.robot.robot import Robot
from offloading_manager.type import OffloadingType, ModuleType, RobotID


class RobotRegistry:
    def __init__(self):
        self._robots_state: dict[Robot, OffloadingType] = {}

    # ------------------- ROBOT STATE ------------------- #

    def change_offloading_state(
        self, robot_id: RobotID, offloading: OffloadingType
    ) -> None:
        """Change the saved offloading state of a robot
        Args:
            robot_id (RobotID): the id of the robot
            offloading (OffloadingType): the new offloading state of the robot
        """
        for robot in self._robots_state.keys():
            if robot.robot_id == robot_id:
                self._robots_state[robot] = offloading
                break

    def get_robot_state(self, robot_id: RobotID) -> OffloadingType | None:
        """Get the saved offloading state of a robot
        Args:
            robot_id (RobotID): the id of the robot
        Returns:
            OffloadingType | None: the saved offloading state of the robot, or None if not found
        """
        for robot in self._robots_state.keys():
            if robot.robot_id == robot_id:
                return self._robots_state[robot]
        return None

    def get_all_robots_state(self) -> dict[RobotID, OffloadingType]:
        """Get the saved offloading state of all robots
        Returns:
            dict[RobotID, OffloadingType]: a dictionary mapping robot ids to their saved offloading state
        """
        result = {}
        for robot in self._robots_state.keys():
            result[robot.robot_id] = self._robots_state[robot]
        return result

    def get_not_offloading_robots(self) -> list[RobotID]:
        """Get the list of robots that are not offloading in any module at the moment
        Returns:
            list[RobotID]: a list of robot ids that are not offloading in any module
        """

        return [
            robot.robot_id
            for robot, state in self._robots_state.items()
            if not (state.aggregate or state.aruco or state.neighbor)
        ]

    def get_offloading_robots_in_module(self, module_type: ModuleType) -> list[RobotID]:
        """Get the list of robots that are offloading in a specific module
        Args:
            module_type (ModuleType): the module of interest
        Returns:
            list[RobotID]: a list of robot ids that are offloading in the specified module
        """

        attr = module_type.value
        return [
            robot.robot_id
            for robot, state in self._robots_state.items()
            if getattr(state, attr)
        ]

    def get_module_for_robot(self, robot_id: RobotID) -> list[ModuleType]:
        """Get the list of modules in which a specific robot is offloading
        Args:
            robot_id (RobotID): the id of the robot
        Returns:
            list[ModuleType]: a list of module types in which the robot is offloading
        """

        modules = []
        for robot, state in self._robots_state.items():
            if robot.robot_id == robot_id:
                if state.aggregate:
                    modules.append(ModuleType.AGGREGATE)
                if state.aruco:
                    modules.append(ModuleType.ARUCO)
                if state.neighbor:
                    modules.append(ModuleType.NEIGHBOR)
        return modules

    def get_robots_ids(self) -> list[RobotID]:
        """Get the list of all robot ids that are currently in the state
        Returns:
            list[RobotID]: a list of all robot ids that are currently in the state
        """

        return [robot.robot_id for robot in self._robots_state.keys()]

    def add_robot_connection(self, robot: Robot) -> None:
        """Add a robot connection to the state
        Args:
            robot (Robot): the robot connection to add
        """

        self._robots_state[robot] = OffloadingType()

    def remove_robot_connection(self, robot_id: RobotID) -> None:
        """Remove a robot connection from the state
        Args:
            robot_id (RobotID): the id of the robot
        """

        for robot in self._robots_state.keys():
            if robot.robot_id == robot_id:
                self._robots_state.pop(robot)
                break

    def get_robot_connection(self, robot_id: RobotID) -> Robot | None:
        """Get a robot connection from the state
        Args:
            robot_id (RobotID): the id of the robot
        Returns:
            Optional[Robot]: the robot connection, or None if not found
        """

        for robot in self._robots_state.keys():
            if robot.robot_id == robot_id:
                return robot
        return None

    def get_drone_offloading_capable(self) -> int:
        """Get the number of robots that offloading capable
        Returns:
            int: the number of robots that are currently offloading in at least one module
        """

        return len(self._robots_state)

    def get_robot_in_module_offloading(self) -> dict[ModuleType, int]:
        """Get the number of robots that are offloading in each module
        Returns:
            dict[ModuleType, int]: a dictionary mapping module types to the number of robots that are currently offloading in that module
        """
        return {
            module: len(self.get_offloading_robots_in_module(module))
            for module in ModuleType
        }
