from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from offloading_manager.routers.json_rpc_wrapper import (
    parse_json_rpc_message, Request, Notification, SuccessResponse, ErrorResponse
)
from offloading_manager.core.state import OffloadingType, offloading_robot_self_request



class Robot:
    def __init__(self, websocket: WebSocket, robot_id: int):
        self.ws = websocket
        self.robot_id = robot_id
        self.connected = False
        self.notification_id = 0
        self.arrived_request = 0

    async def connect(self):
        await self.ws.accept()
        self.connected = True
    
    async def disconnect(self):
        self.connected = False

    async def listen(self):
        try:
            while WebSocketDisconnect:
                data = await self.ws.receive_text()   
                mesage = await self.parse_json(data)
                if isinstance(mesage, Request):
                    try:
                        offloading_request = OffloadingType.model_validate(mesage.params)
                        await offloading_robot_self_request(self.robot_id, offloading_request)
                        self.arrived_request = mesage.id
                    except ValidationError as e:
                        await self.ws.send_json(ErrorResponse(jsonrpc=2.0, error={"code": -32700, "message": "Parse error"}, id=mesage.id).model_dump())
        except Exception:
            pass 

    async def change_status_request(self, data: str):
        if self.connected:
            await self.ws.send_json(Request(jsonrpc=2.0, method="change_status", params=data, id=self.notification_id).model_dump())
            self.notification_id += 1

    async def acknowledged(self, data: str):
        if self.connected:
            await self.ws.send_json(SuccessResponse(jsonrpc=2.0, result=data, id=self.arrived_request).model_dump())

    async def parse_json(self, data: str):
        try :
            return parse_json_rpc_message(data)
        except (ValueError, ValidationError) as e:
            await self.ws.send_json({"error": str(e)}) 
        