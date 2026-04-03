from offloading_manager.routers.robot.robot import Robot
from offloading_manager.routers.module.module import Module
from offloading_manager.type import OffloadingType, ModuleType, Stats
from typing import Dict, Optional

class State:
    def __init__(self):
        self._robots_state: Dict[int, OffloadingType] = {}
        self._robots_connection: Dict[int, Robot] = {}
        self._module_connections: Dict[ModuleType, Module] = {}
        self._module_stats: Dict[ModuleType, Stats] = {}

    # ------------------- ROBOT STATE ------------------- #

    def change_offloading_state(self, robot_id: int, offloading: OffloadingType) -> None:
        """Change the saved offloading state of a robot
        Args:
            robot_id (int): the id of the robot
            offloading (OffloadingType): the new offloading state of the robot
        """

        self._robots_state[robot_id] = offloading

    def remove_robot_state(self, robot_id: int) -> None:
        """Remove the saved offloading state of a robot
        Args:
            robot_id (int): the id of the robot
        """

        self._robots_state.pop(robot_id, None)
        
    def get_robot_state(self, robot_id: int) -> Optional[OffloadingType]:
        """Get the saved offloading state of a robot
        Args:
            robot_id (int): the id of the robot
        Returns:
            Optional[OffloadingType]: the saved offloading state of the robot, or None if not found
        """

        return self._robots_state.get(robot_id)
    
    def get_all_robots_state(self) -> Dict[int, OffloadingType]:
        """Get the saved offloading state of all robots
        Returns:
            Dict[int, OffloadingType]: a dictionary mapping robot ids to their saved offloading state
        """

        return self._robots_state

    def get_not_offloading_robots(self) -> list[int]:
        """Get the list of robots that are not offloading in any module at the moment
        Returns:
            list[int]: a list of robot ids that are not offloading in any module
        """

        return [
            robot_id
            for robot_id, state in self._robots_state.items()
            if not (state.aggregate or state.aruco or state.neighbor)
        ]

    def get_offloading_robots_in_module(self, module_type: ModuleType) -> list[int]:
        """Get the list of robots that are offloading in a specific module
        Args:
            module_type (ModuleType): the module of interest
        Returns:
            list[int]: a list of robot ids that are offloading in the specified module
        """

        attr = module_type.value  
        return [
            robot_id
            for robot_id, state in self._robots_state.items()
            if getattr(state, attr)
        ]
    
    def get_module_for_robot(self, robot_id: int) -> list[ModuleType]:
        """Get the list of modules in which a specific robot is offloading
        Args:
            robot_id (int): the id of the robot
        Returns:
            list[ModuleType]: a list of module types in which the robot is offloading
        """

        modules = []
        if robot_id in self._robots_state:
            state = self._robots_state[robot_id]
            if state.aggregate:
                modules.append(ModuleType.AGGREGATE)
            if state.aruco:
                modules.append(ModuleType.ARUCO)
            if state.neighbor:
                modules.append(ModuleType.NEIGHBOR)
        return modules

    # ------------------- ROBOT CONNECTIONS ------------------- #

    def add_robot_connection(self, robot_id: int, robot: Robot) -> None:
        """Add a robot connection to the state
        Args:
            robot_id (int): the id of the robot
            robot (Robot): the robot connection to add
        """

        self._robots_connection[robot_id] = robot

    def remove_robot_connection(self, robot_id: int) -> None:
        """Remove a robot connection from the state
        Args:
            robot_id (int): the id of the robot
        """

        self._robots_connection.pop(robot_id, None)

    def get_robot_connection(self, robot_id: int) -> Optional[Robot]:
        """Get a robot connection from the state
        Args:
            robot_id (int): the id of the robot
        Returns:
            Optional[Robot]: the robot connection, or None if not found
        """

        return self._robots_connection.get(robot_id)

    # ------------------- MODULE CONNECTIONS ------------------- #

    def add_module_connection(self, module_type: ModuleType, module: Module) -> None:
        """Add a module connection to the state
        Args:
            module_type (ModuleType): the type of the module
            module (Module): the module connection to add
        """

        self._module_connections[module_type] = module

    def get_module_connection(self, module_type: ModuleType) -> Optional[Module]:
        """Get a module connection from the state
        Args:
            module_type (ModuleType): the type of the module
        Returns:
            Optional[Module]: the module connection, or None if not found
        """

        return self._module_connections.get(module_type)

    # ------------------- STATS ------------------- #

    def update_module_stats(self, module_type: ModuleType, stats: Stats) -> None:
        """Update the saved stats of a module
        Args:
            module_type (ModuleType): the type of the module
            stats (Stats): the new stats to save for the module
        """

        self._module_stats[module_type] = stats

    def get_modules_stats(self) -> Dict[ModuleType, Stats]:
        """Get the saved stats of all modules
        Returns:
            Dict[ModuleType, Stats]: a dictionary mapping module types to their saved stats
        """

        return self._module_stats

    def get_drone_offloading_capable(self) -> int:
        """Get the number of robots that offloading capable
        Returns:
            int: the number of robots that are currently offloading in at least one module
        """

        return len(self._robots_connection)

    def get_robot_in_module_offloading(self) -> dict[ModuleType, int]:
        """Get the number of robots that are offloading in each module
        Returns:
            dict[ModuleType, int]: a dictionary mapping module types to the number of robots that are currently offloading in that module
        """
        return {module: len(self.get_offloading_robots_in_module(module)) for module in ModuleType}
        

state = State()

def get_state() -> State:
    return state