from pydantic import BaseModel, Field
from typing import Literal

class MethodSwitch(BaseModel):
    method: Literal["equal_payment", "equal_principal"]
    note: str | None = Field(default=None, max_length=200)
