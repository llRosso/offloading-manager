from pydantic import BaseModel

class ChangeState(BaseModel):
    id: int
    calc: bool