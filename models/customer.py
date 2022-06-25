from redis_om import (Field, JsonModel)
from typing import Optional, List


class Customer(JsonModel):
    name: str = Field(index=True)
    description: Optional[str] = Field(index=False)
    email: str = Field(index=True)
    client_tags: List[str] = Field(index=True)
