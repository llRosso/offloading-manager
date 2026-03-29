from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .module import Module
from offloading_manager.core.state import add_module_connection, Module_Type


modules_router = APIRouter()

@modules_router.websocket("/ws/position")
async def position_websoket(websocket: WebSocket):
        position_websoket = Module(websocket)
        add_module_connection(Module_Type.ARUCO, position_websoket)
        await position_websoket.connect()
        try:
            await position_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await position_websoket.disconnect()

@modules_router.websocket("/ws/aggregate")
async def aggregate_websoket(websocket: WebSocket):
        aggregate_websoket = Module(websocket)
        add_module_connection(Module_Type.AGGREGATE, aggregate_websoket)
        await aggregate_websoket.connect()
        try:
            await aggregate_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await aggregate_websoket.disconnect()

@modules_router.websocket("/ws/neighboor")
async def neighboor_websoket(websocket: WebSocket):
        neighboor_websoket = Module(websocket)
        add_module_connection(Module_Type.NEIGHBOR, neighboor_websoket)
        await neighboor_websoket.connect()
        try:
            await neighboor_websoket.listen()          
        except WebSocketDisconnect:
            pass
        finally:
            await neighboor_websoket.disconnect()

