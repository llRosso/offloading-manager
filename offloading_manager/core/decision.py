from offloading_manager.core.state import OffloadingType
from offloading_manager.routers.state.models import RequestResponse

async def offloading_consideration(robot_id: int, request_type: OffloadingType) -> RequestResponse:
    #impl offloading request to robot 
    return RequestResponse(success=True, message="ok")
