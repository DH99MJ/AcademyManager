from typing import List
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import date
from .dependencies import is_student



router = APIRouter(
    prefix='/student-grades',
    tags=['Student Grade']
)


@router.get('/', response_model=List[schemas.ResponseGrade])
def get_own_grades(db: Session = Depends(get_db), student_id: int = Depends(is_student)):

    # Fetch grades and course information for the specific student
    grades = db.query(
        models.Grade.id,
        models.Grade.student_id,
        models.Grade.course_id,
        models.Grade.grade,
        models.Grade.comments,
        models.Grade.graded_at,
        models.Course.course_name  # Fetch course_name from the Course table
    ).join(
        models.Course, models.Course.id == models.Grade.course_id  # Join with the Course table
    ).filter(
        models.Grade.student_id == student_id  # Use current_user_id from dependency
    ).all()

    # Check if any grades are returned
    if not grades:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No grades found for the student with id={student_id}")

    # Map to ResponseGrade schema
    return [
        schemas.ResponseGrade(
            id=grade.id,
            student_id=grade.student_id,
            course_id=grade.course_id,
            course_name=grade.course_name,
            grade=grade.grade,
            comments=grade.comments,
            graded_at=grade.graded_at.date()
        )
        for grade in grades
    ]
