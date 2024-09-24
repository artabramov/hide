
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CustomExecuteRequest(BaseModel):
    params: Dict[str, Any]
