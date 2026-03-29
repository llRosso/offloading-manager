from fastapi import APIRouter, HTTPException
from .models import SystemStatusResponse
from offloading_manager.core.state import get_module_stats, Module_Type, get_drone_offloading_capable

system_router = APIRouter()

@system_router.get("/stress/system")
async def get_system_stress() -> SystemStatusResponse:
    module_stats = get_module_stats() 
    return SystemStatusResponse(
        cpu_usage={module_type: stats.cpu_usage for module_type, stats in module_stats.items()},
        memory_usage={module_type: stats.memory_usage for module_type, stats in module_stats.items()},
        offloading_capable_robot=get_drone_offloading_capable(),
        robot_in_offloading={module_type: stats.drone_in_offloading for module_type, stats in module_stats.items()}
    )
    