from typing import Any
from enum import Enum
from pydantic import BaseModel
import json

class JsonRPCtype(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR_RESPONSE = "error_response"

class SuccessResponse(BaseModel):
    jsonrpc: float
    id: int
    result: Any

class Request(BaseModel):   
    jsonrpc: float
    method: str
    params: Any
    id: int
           
class Notification(BaseModel):
    jsonrpc: float
    method: str
    params: Any

class ErrorResponse(BaseModel):
    jsonrpc: float
    error: dict
    id: int

JsonRPCMessage = Request | Notification | SuccessResponse | ErrorResponse

def parse_json_rpc_message(raw: str) -> JsonRPCMessage:
    data = json.loads(raw)

    if "method" in data and "id" in data:
        return Request.model_validate(data)
    elif "method" in data:
        return Notification.model_validate(data)
    elif "result" in data:
        return SuccessResponse.model_validate(data)
    elif "error" in data:
        return ErrorResponse.model_validate(data)
    else:
        raise ValueError(f"Messaggio JSON-RPC non riconosciuto: {data}")