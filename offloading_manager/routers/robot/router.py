from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .robot import Robot
from offloading_manager.core.state import add_robot_connection, remove_robot_connection

robots_router = APIRouter()


@robots_router.websocket("/ws/robots/{robot_id}")
async def robot_websocket(websocket: WebSocket, robot_id: int):
    robot = Robot(websocket, robot_id)
    await robot.connect()

    add_robot_connection(robot_id, robot)

    try:
        await robot.listen()          
    except WebSocketDisconnect:
        pass
    finally:
        remove_robot_connection(robot_id)
        await robot.disconnect()