from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from .robot import Robot
from offloading_manager.core.state import get_state, State

robots_router = APIRouter()

@robots_router.websocket("/ws/robots/{robot_id}")
async def robot_websocket(websocket: WebSocket, robot_id: int, state: State = Depends(get_state)):
    robot = Robot(websocket, robot_id, state)
    await robot.connect()
    
    try:
        await robot.listen()          
    except WebSocketDisconnect:
        pass
    finally:
        state.remove_robot_connection(robot_id)
        await robot.disconnect()