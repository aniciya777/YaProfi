from typing import Optional

from pydantic import BaseModel


class StudentBase(BaseModel):
    name: Optional[str] = None
    email: str
    group_id: int


class StudentUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    group_id: Optional[int] = None


class StudentOut(BaseModel):
    id: int
    group_id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True
