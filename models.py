from typing import Literal, Optional
from pydantic import BaseModel


class MyAction(BaseModel):
    label: Optional[Literal["spam", "personal", "work", "urgent"]] = None
    summary: Optional[str] = None
    reply: Optional[str] = None
    department: Optional[Literal[
        "engineering", "support", "sales", "billing",
        "marketing", "legal", "security", "management", "none"
    ]] = None


class MyObservation(BaseModel):
    email: str
    done: bool
    reward: float
    metadata: dict = {}
