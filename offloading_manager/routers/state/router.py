from fastapi import APIRouter, HTTPException
import asyncio
from offloading_manager.core.state import get_robot_state, get_all_robots_state, offloading_request
from .models import (
    RobotStatusResponse,
    StatusResponse,
    RequestResponse,
    OffloadingRequest
)

state_router = APIRouter()

response_wait = asyncio.Future()

@state_router.get("/")
async def get_all_offloading_status() -> StatusResponse:
    return StatusResponse(robots=get_all_robots_state())

@state_router.get("/{robot_id}")
async def get_robot_status(robot_id: int) -> RobotStatusResponse:
    robot_state = get_robot_state(robot_id)
    if not robot_state:
        raise HTTPException(status_code=404, detail="Robot not found")
    return RobotStatusResponse(id=robot_id, state=robot_state)

@state_router.put("/{robot_id}")
async def put_robot_status(robot_id: int, body: OffloadingRequest) -> RequestResponse:
    return await offloading_request(robot_id, body.type)

