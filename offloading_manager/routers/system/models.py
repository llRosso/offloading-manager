from pydantic import BaseModel
from offloading_manager.type import ModuleType

class SystemStatusResponse(BaseModel):
    cpu_usage: dict[ModuleType, float]
    memory_usage: dict[ModuleType, float]
    offloading_capable_robot: int
    robot_in_offloading: dict[ModuleType, int]