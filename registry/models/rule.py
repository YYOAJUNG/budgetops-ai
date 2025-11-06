from pydantic import BaseModel
from typing import Optional

class RuleMetadata(BaseModel):
    rule_id: str
    version: int
    scope: str
    description: Optional[str] = None
