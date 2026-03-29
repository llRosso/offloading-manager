from pydantic import BaseModel
from offloading_manager.core.state import Module_Type

class SystemStatusResponse(BaseModel):
    cpu_usage: dict[Module_Type, float]
    memory_usage: dict[Module_Type, float]
    offloading_capable_robot: int
    robot_in_offloading: dict[Module_Type, int]