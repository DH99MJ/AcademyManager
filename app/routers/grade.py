from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_teacher, teacher_verify_course
from datetime import date

router = APIRouter(
    prefix="/teachers",
    tags=['Grades']
)

@router.post('/grades/user_id/{user_id}', status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseGrade)
def create_grade(grade: schemas.CreateGrade, db: Session = Depends(get_db), teacher_id = Depends(is_teacher)):

    # Validate that the course exists
    course = db.query(models.Course).filter(models.Course.id == grade.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {grade.course_id} does not exist"
        )

    # Validate that the student exists
    student = db.query(models.Student).filter(models.Student.id == grade.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {grade.student_id} does not exist"
        )

    # Use the existing function to verify if the teacher is assigned to the course and student
    teacher_verify_course(teacher_id, grade.student_id, grade.course_id, db)

    # Check for duplicate grade for this student and course
    duplicate_record = db.query(models.Grade).filter(
        models.Grade.student_id == grade.student_id,
        models.Grade.course_id == grade.course_id
    ).first()

    if duplicate_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Grade for student {grade.student_id} in course {grade.course_id} already exists"
        )

    # Create a new grade
    new_grade = models.Grade(**grade.dict())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)

    # Return response with `graded_at` as a date
    return schemas.ResponseGrade(
        id=new_grade.id,
        student_id=new_grade.student_id,
        course_id=new_grade.course_id,
        grade=new_grade.grade,
        comments=new_grade.comments,
        graded_at=new_grade.graded_at.date()  # Convert `graded_at` to a date
    )



@router.put('/grades/{grade_id}/users/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.ResponseGrade)
def update_grade(grade_id: int, user_id: int,grade: schemas.UpdateGrade, db: Session = Depends(get_db), teacher_id: int = Depends(is_teacher)):

    # Fetch the existing grade based on 'grade_id'
    existing_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()

    if not existing_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The grade with id={grade_id} does not exist"
        )

    # Verify that the teacher (user_id) is assigned to the student and course
    teacher_verify_course(user_id, existing_grade.student_id, existing_grade.course_id, db)

    # Update only the fields that are provided in the request
    if grade.grade is not None:
        existing_grade.grade = grade.grade
    if grade.comments is not None:
        existing_grade.comments = grade.comments

    # Commit changes to the database
    db.commit()
    db.refresh(existing_grade)

    # Return the updated grade and convert 'graded_at' to a date
    return schemas.ResponseGrade(
        id=existing_grade.id,
        student_id=existing_grade.student_id,
        course_id=existing_grade.course_id,
        grade=existing_grade.grade,
        comments=existing_grade.comments,
        graded_at=existing_grade.graded_at.date()  # Hardcoded conversion to date
    )

@router.delete('/grades/{grade_id}/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(grade_id: int, user_id: int, db: Session = Depends(get_db), teacher_id = Depends(is_teacher)):

    # Fetch the existing grade by 'grade_id'
    existing_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()

    if not existing_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The grade with id={grade_id} does not exist"
        )

    # Ensure the teacher is assigned to the course and student for deletion
    teacher_verify_course(teacher_id, existing_grade.student_id, existing_grade.course_id, db)

    # Delete the grade
    db.delete(existing_grade)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)