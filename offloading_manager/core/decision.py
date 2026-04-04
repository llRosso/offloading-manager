from __future__ import annotations
from offloading_manager.type import OffloadingType
from offloading_manager.routers.state.models import RequestResponse
from offloading_manager.routers.robot.models import OffloadingRequest
from offloading_manager.routers.module.models import ChangeState
from offloading_manager.type import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State

async def offloading_request_consideration(robot_id: int, request_type: OffloadingType, state: State) -> RequestResponse:
    """Considers an offloading request from a robot, updates the offloading state, and notifies the relevant modules.
    Args:
        robot_id (int): the id of the robot making the request
        request_type (OffloadingType): the requested offloading state for the robot
        state (State): the current state of the system
    Returns:
        RequestResponse: the result of the offloading request consideration, indicating success or failure
    """
    
    robot_connection = state.get_robot_connection(robot_id)
    if robot_connection is not None:
        result = await robot_connection.change_status_request(OffloadingRequest(id=robot_id, type=request_type))
        if result is not None:
            if result:
                for module in ModuleType:
                    module_connection = state.get_module_connection(module)
                    if module_connection is not None:
                        if getattr(request_type, module.value):
                            await module_connection.change_status_request(ChangeState(id=robot_id, calc=True))
                        else:
                            await module_connection.change_status_request(ChangeState(id=robot_id, calc=False))
                state.change_offloading_state(robot_id, request_type)
            return RequestResponse(success=result)
    return RequestResponse(success=False)

async def offloading_self_request_consideration(robot_id: int, request_type: OffloadingType, state: State, message_id: int) -> None: 
    """Considers an offloading request initiated by the robot itself, updates the offloading state, and notifies the relevant modules.
    Args:        
        robot_id (int): the id of the robot making the request
        request_type (OffloadingType): the requested offloading state for the robot
        state (State): the current state of the system
        message_id (int): the id of the incoming message to respond to
    """
    
    for module in ModuleType:
        module_connection = state.get_module_connection(module)
        if module_connection is not None:
            if getattr(request_type, module.value):
                await module_connection.change_status_request(ChangeState(id=robot_id, calc=True))
            else:
                await module_connection.change_status_request(ChangeState(id=robot_id, calc=False))
    state.change_offloading_state(robot_id, request_type)
    robot_connection = state.get_robot_connection(robot_id)
    if robot_connection:
        await robot_connection.respond(True, message_id)

async def stats_valutation(state: State):
    """Evaluates the current system stats and, if any module is under high stress, tries to remove robots from offloading in that module until the stress is reduced.
    Args:        
        state (State): the current state of the system
    """

    all_stats = state.get_modules_stats()
    for module, stats in all_stats.items():
        if stats.cpu_usage > 80 or stats.memory_usage > 80:
            for robot_id in state.get_robots_ids():
                if await remove_robot_from_offloading(state.get_offloading_robots_in_module(module)[robot_id], module, state):
                    break
            #per il momento in caso di stress parte a provare a togliere il primo robot fin quando non ci riesce
            
async def remove_robot_from_offloading(robot_id: int, module_type: ModuleType, state: State) -> bool | None:
    """Removes a robot from offloading in a specific module, updates the offloading state, and notifies the relevant modules.
    Args:        
        robot_id (int): the id of the robot to remove from offloading
        module_type (ModuleType): the module from which to remove the robot from offloading
        state (State): the current state of the system
    Returns:
        bool | None: the result of the operation, or None if the robot was not offloading in the specified module or if the operation failed
    """
    
    offloading_module = state.get_robot_state(robot_id)
    if offloading_module is not None: 
        offloading_request = offloading_module.model_copy(update={module_type.value: False})     
        result = await offloading_request_consideration(robot_id, offloading_request, state)
        return result.success

