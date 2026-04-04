from pydantic import BaseModel


class MyAction(BaseModel):
    label: str | None = None
    summary: str | None = None
    reply: str | None = None


class MyObservation(BaseModel):
    email: str
    done: bool
    reward: float
    metadata: dict = {}
