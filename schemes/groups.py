from typing import Optional, List

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: Optional[str] = ''
    parent_id: Optional[int] = None


class GroupUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    parent_id: Optional[int] = None


class GroupOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class GroupOutWithoutParent(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# Для вывода иерархического дерева групп
class GroupTree(BaseModel):
    id: int
    name: str
    subGroups: List["GroupTree"] = []

    class Config:
        from_attributes = True


GroupTree.model_rebuild()
