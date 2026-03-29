from pydantic import BaseModel
from offloading_manager.routers.robot.robot import Robot
from offloading_manager.routers.module.module import Module
from offloading_manager.core.decision import offloading_consideration
from enum import Enum

class OffloadingType(BaseModel):
    aggregate : bool = False
    aruco : bool = False
    neighbor : bool = False

class OffloadingState(BaseModel):
    aggregate : bool = False
    aruco : bool = False
    neighbor : bool = False
    available : bool = True

robots_state: dict[int, OffloadingState] = {}

robot_requests: dict[int, OffloadingType] = {}

robots_connection: dict [int , Robot] = {}

class Module_Type(Enum):
    AGGREGATE = "aggregate"
    ARUCO = "aruco"
    NEIGHBOR = "neighbor"

module_connections: dict[Module_Type, Module] = {}

class Stasts(BaseModel):
    cpu_usage: float
    memory_usage: float
    drone_in_offloading: int

module_stats: dict[Module_Type, Stasts] = {}
drone_offloading_capable: int = 0


#-------------------ROBOT STATE------------------#

def robot_unavailable(id: int):
    robots_state[id].available = False

def change_offloading_state(id: int, offloading: OffloadingState):
    state = robots_state[id]
    update_data = offloading.model_dump(exclude_unset=True) 
    for field, value in update_data.items():
        setattr(state, field, value)

def get_robot_state(id: int) -> OffloadingState | None:
    return robots_state.get(id)

def get_all_robots_state() -> dict[int, OffloadingState]:
    return robots_state

async def offloading_request(id: int, offloading: OffloadingType) :
    robot_requests[id] = offloading
    return await offloading_consideration(id, offloading)

async def offloading_robot_self_request(id: int, offloading: OffloadingType) :
    robot_requests[id] = offloading
    await offloading_consideration(id, offloading)
    #to consider request from the robot

#-------------------ROBOT CONNECTIONS------------------#

def add_robot_connection(id: int, robot: Robot):
    robots_connection[id] = robot

def remove_robot_connection(id: int):
    robots_connection.pop(id, None)

def get_robot_connection(id: int) -> Robot | None:
    return robots_connection.get(id)

#-------------------MODULE CONNECTIONS------------------#

def add_module_connection(module_type: Module_Type, module: Module):
    module_connections[module_type] = module

#-------------------STATS------------------#

def update_module_stats(module_type: Module_Type, stats: Stasts):
    module_stats[module_type] = stats

def get_module_stats() -> dict[Module_Type, Stasts] :
    return module_stats

def get_drone_offloading_capable() -> int:
    return drone_offloading_capable
