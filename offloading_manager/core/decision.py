from offloading_manager.type import OffloadingType
from offloading_manager.routers.state.models import RequestResponse
from .state import State
from offloading_manager.routers.robot.models import OffloadingRequest
from offloading_manager.routers.module.models import ChangeState
from offloading_manager.type import ModuleType

async def offloading_request_consideration(robot_id: int, request_type: OffloadingType, state: State) -> RequestResponse:
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
    all_stats = state.get_modules_stats()
    for module, stats in all_stats.items():
        if stats.cpu_usage > 80 or stats.memory_usage > 80:
            i = 0
            while not await remove_robot_from_offloading(state.get_offloading_robots_in_module(module)[i], module, state):
                i += 1
            #per il momento in caso di stress parte a provare a togliere il primo robot fin quando non ci riesce
            
async def remove_robot_from_offloading(robot_id: int, module_type: ModuleType, state: State) -> bool | None:
    offloading_module = state.get_robot_state(robot_id)
    if offloading_module is not None: 
        offloading_request = offloading_module.copy(update={module_type.value: False})     
        result = await offloading_request_consideration(robot_id, offloading_request, state)
        return result.success

