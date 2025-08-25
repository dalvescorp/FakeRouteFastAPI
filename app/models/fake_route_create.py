from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class FakeRouteCreate(BaseModel):
    name: str
    return_value: Dict[str, Any] = Field(..., alias="return")
    status_code: int = 200
    headers: Optional[Dict[str, str]] = None
    delay: float = 0.0
    methods: list[str]
