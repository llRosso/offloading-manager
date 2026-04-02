from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from .module import Module
from offloading_manager.core.state import State, get_state
from offloading_manager.type import ModuleType


modules_router = APIRouter()

@modules_router.websocket("/ws/position")
async def position_websoket(websocket: WebSocket, state: State = Depends(get_state)):
        position_websoket = Module(websocket)
        state.add_module_connection(ModuleType.ARUCO, position_websoket)
        await position_websoket.connect()
        try:
            await position_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await position_websoket.disconnect()

@modules_router.websocket("/ws/aggregate")
async def aggregate_websoket(websocket: WebSocket, state: State = Depends(get_state)):
        aggregate_websoket = Module(websocket)
        state.add_module_connection(ModuleType.AGGREGATE, aggregate_websoket)
        await aggregate_websoket.connect()
        try:
            await aggregate_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await aggregate_websoket.disconnect()

@modules_router.websocket("/ws/neighboor")
async def neighboor_websoket(websocket: WebSocket, state: State = Depends(get_state)):
        neighboor_websoket = Module(websocket)
        state.add_module_connection(ModuleType.NEIGHBOR, neighboor_websoket)
        await neighboor_websoket.connect()
        try:
            await neighboor_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await neighboor_websoket.disconnect()

