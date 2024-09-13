from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_admin
from datetime import date

router = APIRouter(
    prefix="/admin",
    tags=['enrollment']
)


@router.post('/enroll-student/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.EnrollmentResponse)
def enroll_student(enroll: schemas.EnrollmentRequest, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Ensure course already exists
    course = db.query(models.Course).filter(models.Course.id == enroll.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id={enroll.course_id} not found")
    
    # Ensure teacher already exists
    teacher = db.query(models.Teacher).filter(models.Teacher.id == enroll.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id={enroll.teacher_id} not found")

    # Ensure the student doesn't enroll with the same course and teacher
    enrollment_student = db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == enroll.student_id,
        models.StudentCourse.teacher_id == enroll.teacher_id,
        models.StudentCourse.course_id  == enroll.course_id
        ).first()
    
    
   # Validate if the student is already enrolled
    if enrollment_student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Student with id={enroll.student_id} is already enrolled in this course with this teacher.")
    

    # Create new enrollment student
    new_enrollment = models.StudentCourse(
        student_id=enroll.student_id,
        course_id=enroll.course_id,
        teacher_id=enroll.teacher_id,
        enrollment_date=enroll.enrollment_date
    )
    
    # Add everything to db
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return schemas.EnrollmentResponse(
        message="Student enrolled successfully.",
        student_id=new_enrollment.student_id,
        course_id=new_enrollment.course_id,
        teacher_id=new_enrollment.teacher_id,
        enrollment_date=new_enrollment.enrollment_date,
        student_info=schemas.PersonalInfo(
            first_name=new_enrollment.student.user.first_name,
            last_name=new_enrollment.student.user.last_name,
            email=new_enrollment.student.user.email
        ),
        teacher_info=schemas.PersonalInfo(
            first_name=new_enrollment.teacher.user.first_name,
            last_name=new_enrollment.teacher.user.last_name,
            email=new_enrollment.teacher.user.email
        )
    )
    


# Fetch all enrollments based on course_id
@router.post('/enroll-student/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.EnrollmentResponse)
def enroll_student(enroll: schemas.EnrollmentRequest, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Ensure the course exists
    course = db.query(models.Course).filter(models.Course.id == enroll.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id={enroll.course_id} not found.")
    
    # Ensure the teacher exists
    teacher = db.query(models.Teacher).filter(models.Teacher.id == enroll.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id={enroll.teacher_id} not found.")
    
    # Ensure the student exists
    student = db.query(models.Student).filter(models.Student.id == enroll.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with id={enroll.student_id} not found.")
    
    # Ensure the student is not already enrolled in the course with the same teacher
    enrollment_exists = db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == enroll.student_id,
        models.StudentCourse.course_id == enroll.course_id,
        models.StudentCourse.teacher_id == enroll.teacher_id
    ).first()

    # Graceful handling if the student is already enrolled
    if enrollment_exists:
        return {
            "message": f"Student with id={enroll.student_id} is already enrolled in course id={enroll.course_id} with teacher id={enroll.teacher_id}."
        }

    # Proceed with enrollment
    new_enrollment = models.StudentCourse(
        student_id=enroll.student_id,
        course_id=enroll.course_id,
        teacher_id=enroll.teacher_id,
        enrollment_date=enroll.enrollment_date
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    # Fetch teacher's details using their user_id
    teacher_user = db.query(models.User).filter(models.User.id == teacher.user_id).first()

    # Fetch student's details using their user_id
    student_user = db.query(models.User).filter(models.User.id == student.user_id).first()

    # Return the correct response with teacher and student information
    return schemas.EnrollmentResponse(
        message="Student enrolled successfully.",
        student_id=new_enrollment.student_id,
        course_id=new_enrollment.course_id,
        teacher_id=new_enrollment.teacher_id,
        enrollment_date=new_enrollment.enrollment_date,
        student_info=schemas.PersonalInfo(
            first_name=student_user.first_name,
            last_name=student_user.last_name,
            email=student_user.email
        ),
        teacher_info=schemas.PersonalInfo(
            first_name=teacher_user.first_name,
            last_name=teacher_user.last_name,
            email=teacher_user.email
        )
    )