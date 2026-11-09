import math
from typing import Generic, TypeVar

from pydantic import BaseModel, computed_field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return math.ceil(self.total / self.page_size)
