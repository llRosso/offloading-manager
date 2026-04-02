from fastapi import APIRouter, HTTPException, Depends
import asyncio
from offloading_manager.core.decision import offloading_request_consideration
from offloading_manager.core.state import get_state, State
from .models import (
    RobotStatusResponse,
    StatusResponse,
    RequestResponse,
    OffloadingRequest
)

state_router = APIRouter()



@state_router.get("/")
async def get_all_offloading_status(state: State = Depends(get_state)) -> StatusResponse:
    return StatusResponse(robots=state.get_all_robots_state())

@state_router.get("/{robot_id}")
async def get_robot_status(robot_id: int, state: State = Depends(get_state)) -> RobotStatusResponse:
    robot_state = state.get_robot_state(robot_id)
    if not robot_state:
        raise HTTPException(status_code=404, detail="Robot not found")
    return RobotStatusResponse(id=robot_id, state=robot_state)

@state_router.put("/{robot_id}")
async def put_robot_status(robot_id: int, body: OffloadingRequest, state: State = Depends(get_state)) -> RequestResponse:
    return await offloading_request_consideration(robot_id, body.type, state)

