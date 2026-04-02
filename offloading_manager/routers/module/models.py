from pydantic import BaseModel
from offloading_manager.type import OffloadingType


class StatusResponse(BaseModel):
    robots: dict[int, OffloadingType]
    

class RobotStatusResponse(BaseModel):
    id: int
    state: OffloadingType

class RequestResponse(BaseModel):
    success: bool
    message: str

class ChangeState(BaseModel):
    id: int
    calc: bool