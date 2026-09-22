from typing import Literal
from pydantic import BaseModel, Field

class MethodUpdate(BaseModel):
    method: Literal["equal_payment", "equal_principal"]
    note: str | None = Field(default=None, max_length=200)
