from pydantic import BaseModel
from offloading_manager.routers.robot.robot import Robot
from offloading_manager.routers.module.module import Module
from offloading_manager.type import OffloadingType, OffloadingType, ModuleType, Stats
from enum import Enum


from typing import Dict, Optional


class State:
    def __init__(self):
        self._robots_state: Dict[int, OffloadingType] = {}
        self._robot_requests: Dict[int, OffloadingType] = {}
        self._robots_connection: Dict[int, Robot] = {}
        self._module_connections: Dict[ModuleType, Module] = {}
        self._module_stats: Dict[ModuleType, Stats] = {}

    # ------------------- ROBOT STATE ------------------- #

    def change_offloading_state(self, robot_id: int, offloading: OffloadingType) -> None:
        self._robots_state[robot_id] = offloading

    def get_robot_state(self, robot_id: int) -> Optional[OffloadingType]:
        return self._robots_state.get(robot_id)

    def get_all_robots_state(self) -> Dict[int, OffloadingType]:
        return self._robots_state

    def get_not_offloading_robots(self) -> list[int]:
        return [
            robot_id
            for robot_id, state in self._robots_state.items()
            if not (state.aggregate or state.aruco or state.neighbor)
        ]

    def get_offloading_robots(self, module_type: ModuleType) -> list[int]:
        attr = module_type.value  
        return [
            robot_id
            for robot_id, state in self._robots_state.items()
            if getattr(state, attr)
        ]
    
    def get_module_for_robot(self, robot_id: int) -> list[ModuleType]:
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

    # ------------------- REQUESTS ------------------- #
    def get_robot_requests(self) -> Dict[int, OffloadingType]:
        return self._robot_requests

    # ------------------- ROBOT CONNECTIONS ------------------- #

    def add_robot_connection(self, robot_id: int, robot: Robot) -> None:
        self._robots_connection[robot_id] = robot

    def remove_robot_connection(self, robot_id: int) -> None:
        self._robots_connection.pop(robot_id, None)

    def get_robot_connection(self, robot_id: int) -> Optional[Robot]:
        return self._robots_connection.get(robot_id)

    # ------------------- MODULE CONNECTIONS ------------------- #

    def add_module_connection(self, module_type: ModuleType, module: Module) -> None:
        self._module_connections[module_type] = module

    def get_module_connection(self, module_type: ModuleType) -> Optional[Module]:
        return self._module_connections.get(module_type)

    # ------------------- STATS ------------------- #

    def update_module_stats(self, module_type: ModuleType, stats: Stats) -> None:
        self._module_stats[module_type] = stats

    def get_module_stats(self) -> Dict[ModuleType, Stats]:
        return self._module_stats

    def get_drone_offloading_capable(self) -> int:
        return len(self._robots_connection)

    def get_robot_in_module_offloading(self) -> dict[ModuleType, int]:
        return {module: len(self.get_offloading_robots(module)) for module in ModuleType}
        

state = State()

def get_state() -> State:
    return state