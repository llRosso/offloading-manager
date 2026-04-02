from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from offloading_manager.routers.json_rpc_wrapper import (
    parse_json_rpc_message, Request, Notification, SuccessResponse, ErrorResponse
)
from .models import ChangeState

class Module():
    def __init__(self, websocket: WebSocket):
        self.ws = websocket
        self.connected = False

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

        except Exception:
            pass 

    
    async def change_status_request(self, data: ChangeState):
        if self.connected:
            await self.ws.send_json(Notification(jsonrpc=2.0, method="change_status", params=data).model_dump())

    async def parse_json(self, data: str):
        try :
            return parse_json_rpc_message(data)
        except (ValueError, ValidationError) as e:
            await self.ws.send_json({"error": str(e)}) 
        