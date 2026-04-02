import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from .models import OffloadingRequest, RequestResponse
from offloading_manager.routers.json_rpc_wrapper import (
    parse_json_rpc_message, Request, SuccessResponse, ErrorResponse
)
from offloading_manager.core.decision import offloading_self_request_consideration

class Robot:
    def __init__(self, websocket: WebSocket, robot_id: int, state):
        self._ws = websocket
        self._robot_id = robot_id
        self._state = state
        self._connected = False
        self._send_request_id = 0
        self._arrived_request = 0
        self._pending_requests: dict[int, asyncio.Future] = {}

    async def connect(self):
        await self._ws.accept()
        self._connected = True
    
    async def disconnect(self):
        self._connected = False
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()

    async def listen(self):
        try:
            while True:
                data = await self._ws.receive_text()   
                mesage = await self._parse_json(data)
                if isinstance(mesage, Request):
                    await self._arrived_request_valutation(mesage)
                elif isinstance(mesage, SuccessResponse):
                    await self._arrived_response_valutation(mesage)
                elif isinstance(mesage, ErrorResponse):
                    await self._arrived_error_valutation(mesage)
        except WebSocketDisconnect:
            await self.disconnect()
        except Exception as e:
            print(f"Robot {self._robot_id} error: {e}")

    async def change_status_request(self, data: OffloadingRequest) -> bool | None:
        if self._connected:
            loop = asyncio.get_event_loop()
            future: asyncio.Future = loop.create_future()
            self._pending_requests[self._send_request_id] = future
            await self._ws.send_json(Request(jsonrpc=2.0, method="change_status", params=data, id=self._send_request_id).model_dump())
            self._send_request_id += 1
            try:
                result = await asyncio.wait_for(future, timeout=10)  # timeout 10 secondi per il momento non so quanto ci mettano i robot, ricordasi di chiedere
                return result.success
            except asyncio.TimeoutError:
                self._pending_requests.pop(self._send_request_id - 1, None)
                return False
            
    async def acknowledged(self, data: str):
        if self._connected:
            await self._ws.send_json(SuccessResponse(jsonrpc=2.0, result=data, id=self._arrived_request).model_dump())
    
    async def _arrived_request_valutation(self,mesage: Request):
        try:
            offloading_request = OffloadingRequest.model_validate(mesage.params)
            await offloading_self_request_consideration(self._robot_id, offloading_request.type, self._state, mesage.id)
            self._arrived_request = mesage.id
        except ValidationError:
            await self._ws.send_json(ErrorResponse(jsonrpc=2.0, error={"code": -32700, "message": "Parse error"}, id=mesage.id).model_dump())

    async def _arrived_response_valutation(self, mesage: SuccessResponse):
        future = self._pending_requests.pop(mesage.id, None)
        if future and not future.done():
            future.set_result(RequestResponse.model_validate(mesage.result))
    
    async def _arrived_error_valutation(self, mesage: ErrorResponse):
        if mesage.id in self._pending_requests:
            future = self._pending_requests.pop(mesage.id, None)
            if future and not future.done():
                future.set_exception(Exception(mesage.error.get("message", "Unknown error")))

    async def _parse_json(self, data: str):
            try :
                return parse_json_rpc_message(data)
            except (ValueError, ValidationError) as e:
                await self._ws.send_json({"error": str(e)}) 