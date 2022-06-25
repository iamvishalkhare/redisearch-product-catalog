from redis_om import (Field, JsonModel, EmbeddedJsonModel)
from typing import Optional, List


class SkuPrice(EmbeddedJsonModel):
    currency: str
    discounted_price: int = Field(index=True)
    mrp: int = Field(index=True)


class Skus(JsonModel):
    company: str = Field(index=True)
    description: Optional[str] = Field(index=True, full_text_search=True)
    image_url: Optional[str] = Field(index=False)
    price: SkuPrice
    ratings: float = Field(index=True)
    sku_id: int = Field(index=True)
    sku_url: str
    tags: List[str] = Field(index=True)
    title: str = Field(index=True, full_text_search=True)
    token: str = Field(index=True)
