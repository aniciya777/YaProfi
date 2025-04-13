import sqlalchemy as sa
from sqlalchemy import orm

from .__db_session import SqlAlchemyBase


class Student(SqlAlchemyBase):
    __tablename__ = 'students'

    id = sa.Column(sa.Integer, primary_key=True, index=True, autoincrement=True)
    name = sa.Column(sa.String, index=True, nullable=True)
    email = sa.Column(sa.String)
    group_id = sa.Column(sa.Integer, sa.ForeignKey("groups.id"), index=True)
    group = orm.relationship("Group", back_populates="students")
