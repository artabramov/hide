
from typing import Any, Dict
from pydantic import BaseModel


class CustomExecuteRequest(BaseModel):
    params: Dict[str, Any]
