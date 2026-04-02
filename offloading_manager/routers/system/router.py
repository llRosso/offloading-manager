from fastapi import APIRouter, HTTPException, Depends
from .models import SystemStatusResponse
from offloading_manager.core.state import get_state, State

system_router = APIRouter()

@system_router.get("/stress/system")
async def get_system_stress(state: State = Depends(get_state)) -> SystemStatusResponse:
    module_stats = state.get_modules_stats()
    return SystemStatusResponse(
        cpu_usage={module_type: stats.cpu_usage for module_type, stats in module_stats.items()},
        memory_usage={module_type: stats.memory_usage for module_type, stats in module_stats.items()},
        offloading_capable_robot=state.get_drone_offloading_capable(),
        robot_in_offloading=state.get_robot_in_module_offloading()##TODO: implement robot in offloading per modulo
    )
    