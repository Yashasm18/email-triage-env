from pydantic import BaseModel
from typing import Optional

class MyAction(BaseModel):
    label: Optional[str] = None
    summary: Optional[str] = None
    reply: Optional[str] = None
    department: Optional[str] = None

class MyObservation(BaseModel):
    email: str
    done: bool
    reward: float
    metadata: dict = {}
