from pydantic import BaseModel
from offloading_manager.type import OffloadingType

class OffloadingRequest(BaseModel):
    id: int
    type: OffloadingType

class RequestResponse(BaseModel):
    success: bool   