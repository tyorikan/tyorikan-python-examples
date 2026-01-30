from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class MetaData(BaseModel):
    page: Optional[int] = None
    total: Optional[int] = None

class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    meta: Optional[MetaData] = None
    error: Optional[str] = None
