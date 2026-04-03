from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from offloading_manager.routers.json_rpc_wrapper import (
    parse_json_rpc_message, Notification
)
from .models import ChangeState

class Module():
    def __init__(self, websocket: WebSocket):
        self._ws = websocket
        self._connected = False

    async def connect(self):
        await self._ws.accept()
        self._connected = True
    
    async def disconnect(self):
        self._connected = False
    
    async def listen(self):
        try:
            while self._connected:
                data = await self._ws.receive_text()
                mesage = await self.parse_json(data)

        except WebSocketDisconnect:
            await self.disconnect()
        except Exception:
            pass 

    async def change_status_request(self, data: ChangeState):
        if self._connected:
            await self._ws.send_json(Notification(jsonrpc=2.0, method="change_status", params=data).model_dump())

    async def parse_json(self, data: str):
        try :
            return parse_json_rpc_message(data)
        except (ValueError, ValidationError) as e:
            await self._ws.send_json({"error": str(e)}) 
        