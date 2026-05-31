from pydantic import BaseModel


class RepetitionEvent(BaseModel):
    timestamp: str
    event: str
    rep: int
    depth_ok: bool
