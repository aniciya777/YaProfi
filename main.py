from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
import uvicorn
from sqlalchemy import or_

from data import __db_session as db_session
from data.students import Student
from data.group import Group
import schemes.groups as schemes_groups
import schemes.students as schemes_students

db_session.global_init("db/database.sqlite")
app = FastAPI(title="Управление пользователями образовательного учреждения")


@app.post("/groups", response_model=schemes_groups.GroupOut)
def create_group(group: schemes_groups.GroupCreate):
    db_sess = db_session.create_session()
    if group.parent_id is not None:
        parent = db_sess.get(Group, group.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Родительская группа не найдена")
    db_group = Group(name=group.name, parent_id=group.parent_id)
    db_sess.add(db_group)
    db_sess.commit()
    return db_group


@app.get("/groups", response_model=List[schemes_groups.GroupTree])
def get_groups(query: Optional[str] = Query(None)):
    db_sess = db_session.create_session()
    if query:
        query_like = f"%{query}%"
        groups = db_sess.query(Group).filter(Group.name.ilike(query_like)).all()
        return [{"id": g.id, "name": g.name} for g in groups]
    else:
        groups = db_sess.query(Group).all()
        group_dict = {g.id: {"id": g.id, "name": g.name, "subGroups": []} for g in groups}
        root = []
        for g in groups:
            if g.parent_id is None:
                root.append(group_dict[g.id])
            else:
                if g.parent_id in group_dict:
                    group_dict[g.parent_id]["subGroups"].append(group_dict[g.id])
        return root


@app.get("/groups/{group_id}", response_model=schemes_groups.GroupOutWithoutParent)
def get_group(group_id: int):
    db_sess = db_session.create_session()
    group = db_sess.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


@app.put("/groups/{group_id}", response_model=schemes_groups.GroupOut)
def update_group(group_id: int, update: schemes_groups.GroupUpdate):
    db_sess = db_session.create_session()
    if group_id != update.id:
        raise HTTPException(status_code=400, detail="ID в пути и теле запроса не совпадают")
    group: Group | None = db_sess.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if update.parent_id is not None:
        if update.parent_id == group_id:
            raise HTTPException(status_code=400, detail="Группа не может быть родительской для самой себя")
        parent = db_sess.get(Group, update.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Родительская группа не найдена")
        group.parent_id = parent.id
    if update.name is not None:
        group.name = update.name
    db_sess.commit()
    db_sess.refresh(group)
    return group


@app.delete("/groups/{group_id}")
def delete_group(group_id: int):
    db_sess = db_session.create_session()
    group = db_sess.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    children = db_sess.query(Group).filter(Group.parent_id == group_id).first()
    if children:
        raise HTTPException(status_code=400, detail="Невозможно удалить группу, у которой есть подгруппы")
    db_sess.delete(group)
    db_sess.commit()
    return {"detail": "Группа удалена"}


@app.get("/students", response_model=List[schemes_students.StudentOut])
def get_students(query: Optional[str] = Query(None)):
    db_sess = db_session.create_session()
    if query:
        query_like = f"%{query}%"
        students = db_sess.query(Student).join(Group).filter(
            or_(
                Student.name.ilike(query_like),
                Group.name.ilike(query_like)
            )
        ).all()
    else:
        students = db_sess.query(Student).all()
    return students


@app.post("/students", response_model=schemes_students.StudentOut)
def create_student(student: schemes_students.StudentBase):
    db_sess = db_session.create_session()
    group = db_sess.get(Group, student.group_id)
    if not group:
        raise HTTPException(status_code=400, detail="Группа не найдена")
    db_student = Student(name=student.name, email=student.email, group_id=student.group_id)
    db_sess.add(db_student)
    db_sess.commit()
    db_sess.refresh(db_student)
    return db_student


@app.get("/students/{student_id}", response_model=schemes_students.StudentOut)
def get_student(student_id: int):
    db_sess = db_session.create_session()
    student = db_sess.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student


@app.put("/students/{student_id}", response_model=schemes_students.StudentOut)
def update_student(student_id: int, update: schemes_students.StudentUpdate):
    db_sess = db_session.create_session()
    if student_id != update.id:
        raise HTTPException(status_code=400, detail="ID в пути и теле запроса не совпадают")
    student = db_sess.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    if update.group_id is not None:
        group: Group | None = db_sess.get(Group, update.group_id)
        if not group:
            raise HTTPException(status_code=400, detail="Группа не найдена")
        student.group_id = group.id
    if update.name is not None:
        student.name = update.name
    db_sess.commit()
    db_sess.refresh(student)
    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db_sess = db_session.create_session()
    student = db_sess.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    db_sess.delete(student)
    db_sess.commit()
    return {"detail": "Студент удалён"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
