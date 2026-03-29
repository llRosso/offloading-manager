from pydantic import BaseModel
from offloading_manager.core.state import OffloadingState, OffloadingType


class StatusResponse(BaseModel):
    robots: dict[int, OffloadingState]
    

class RobotStatusResponse(BaseModel):
    id: int
    state: OffloadingState

class RequestResponse(BaseModel):
    success: bool
    message: str

class OffloadingRequest(BaseModel):
    id: int
    type: OffloadingType