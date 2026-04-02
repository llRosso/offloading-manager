from pydantic import BaseModel
from offloading_manager.type import OffloadingType, OffloadingType



class StatusResponse(BaseModel):
    robots: dict[int, OffloadingType]
    

class RobotStatusResponse(BaseModel):
    id: int
    state: OffloadingType

class RequestResponse(BaseModel):
    success: bool

class OffloadingRequest(BaseModel):
    id: int
    type: OffloadingType