import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from .models import OffloadingRequest, RequestResponse
from offloading_manager.routers.json_rpc_wrapper import (
    parse_json_rpc_message, Request, Notification, SuccessResponse, ErrorResponse
)
from offloading_manager.type import OffloadingType



class Robot:
    def __init__(self, websocket: WebSocket, robot_id: int, state):
        self.ws = websocket
        self.robot_id = robot_id
        self.state = state
        self.connected = False
        self.notification_id = 0
        self.arrived_request = 0
        self._pending_requests: dict[int, asyncio.Future] = {}

    async def connect(self):
        await self.ws.accept()
        self.connected = True
    
    async def disconnect(self):
        self.connected = False
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()

    async def listen(self):
        try:
            while True:
                data = await self.ws.receive_text()   
                mesage = await self.parse_json(data)
                if isinstance(mesage, Request):
                    try:
                        offloading_request = OffloadingType.model_validate(mesage.params)
                        await self.state.offloading_request(self.robot_id, offloading_request)
                        self.arrived_request = mesage.id
                    except ValidationError as e:
                        await self.ws.send_json(ErrorResponse(jsonrpc=2.0, error={"code": -32700, "message": "Parse error"}, id=mesage.id).model_dump())
                elif isinstance(mesage, SuccessResponse):
                    future = self._pending_requests.pop(mesage.id, None)
                    if future and not future.done():
                        future.set_result(RequestResponse.model_validate(mesage.result))
                elif isinstance(mesage, ErrorResponse):
                    if mesage.id in self._pending_requests:
                        future = self._pending_requests.pop(mesage.id, None)
                        if future and not future.done():
                            future.set_exception(Exception(mesage.error.get("message", "Unknown error")))
        except WebSocketDisconnect:
            await self.disconnect()
        except Exception as e:
            print(f"Robot {self.robot_id} error: {e}")

    async def change_status_request(self, data: OffloadingRequest) -> bool | None:
        if self.connected:
            loop = asyncio.get_event_loop()
            future: asyncio.Future = loop.create_future()
            self._pending_requests[self.notification_id] = future
            await self.ws.send_json(Request(jsonrpc=2.0, method="change_status", params=data, id=self.notification_id).model_dump())
            self.notification_id += 1
            try:
                result = await asyncio.wait_for(future, timeout=10)  # timeout 10 secondi per il momento non so quanto ci mettano i robot, ricordasi di chiedere
                return result.success
            except asyncio.TimeoutError:
                self._pending_requests.pop(self.notification_id - 1, None)
                return False
            
    async def acknowledged(self, data: str):
        if self.connected:
            await self.ws.send_json(SuccessResponse(jsonrpc=2.0, result=data, id=self.arrived_request).model_dump())

    async def parse_json(self, data: str):
        try :
            return parse_json_rpc_message(data)
        except (ValueError, ValidationError) as e:
            await self.ws.send_json({"error": str(e)}) 
        