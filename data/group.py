import sqlalchemy as sa
from sqlalchemy import orm

from .__db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'

    id: int = sa.Column(sa.Integer, primary_key=True, index=True, autoincrement=True)
    name: str = sa.Column(sa.String, index=True, nullable=True)
    parent_id: int = sa.Column(sa.Integer, sa.ForeignKey("groups.id"), nullable=True)

    # parent = orm.relationship("Group", back_populates="children")
    children = orm.relationship("Group", backref="parent", remote_side=[id])
    students = orm.relationship("Student", back_populates="group")

    def __str__(self) -> str:
        return f'<Group {self.id}: {self.name} {self.parent_id}>'