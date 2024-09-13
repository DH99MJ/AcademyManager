from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_teacher, teacher_verify_course
from datetime import date

router = APIRouter(
    prefix="/teachers",
    tags=['Attendance']
)



@router.post('/attendance/user_id/{user_id}', status_code=status.HTTP_201_CREATED, response_model=schemas.AttendanceResponse)
def create_attendance(user: schemas.AttendanceRequest, user_id: int, db: Session = Depends(get_db)):
    
    # Fetch teacher_id from user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == user_id).first()
    
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No teacher found with user_id={user_id}")

    # Verify if the teacher is assigned to the student and course
    course_assignment = db.query(models.StudentCourse).filter(
        models.StudentCourse.teacher_id == teacher.id,
        models.StudentCourse.student_id == user.student_id,
        models.StudentCourse.course_id == user.course_id
    ).first()

    if not course_assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher {teacher.id} is not assigned to student {user.student_id} for course {user.course_id}.")

    # Check if the attendance record already exists
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == user.student_id,
        models.Attendance.course_id == user.course_id
    ).first()

    if existing_attendance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Attendance record for student {user.student_id} in course {user.course_id} already exists.")

    # Create new attendance record
    new_attendance = models.Attendance(
        student_id=user.student_id,
        course_id=user.course_id,
        status=user.status
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    # Fetch the student's details for response
    student = db.query(models.Student).filter(models.Student.id == new_attendance.student_id).first()
    user_info = db.query(models.User).filter(models.User.id == student.user_id).first()

    # Return response
    return schemas.AttendanceResponse(
        id=new_attendance.id,
        student_id=student.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        email=user_info.email,
        course_id=new_attendance.course_id,
        attendance_date=new_attendance.attendance_date.date() if new_attendance.attendance_date else date.today(),
        status=new_attendance.status
    )



@router.put('/attendance/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.AttendanceResponse)
def update_attendance(user_id: int, user: schemas.AttendanceRequest, db: Session = Depends(get_db)):
    # Step 1: Get the teacher_id based on user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == user_id).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No teacher found with user_id {user_id}."
        )

    # Step 2: Verify if the teacher is assigned to the student and course
    course_assignment = db.query(models.StudentCourse).filter(
        models.StudentCourse.teacher_id == teacher.id,  # Now using teacher.id
        models.StudentCourse.student_id == user.student_id,
        models.StudentCourse.course_id == user.course_id
    ).first()

    if not course_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with user_id {user_id} (teacher_id {teacher.id}) is not assigned to student {user.student_id} for course {user.course_id}."
        )

    # Step 3: Check if the attendance record exists for this student and course
    attendance_record = db.query(models.Attendance).filter(
        models.Attendance.student_id == user.student_id,
        models.Attendance.course_id == user.course_id
    ).first()

    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record for student {user.student_id} in course {user.course_id} does not exist."
        )

    # Step 4: Validate and update the attendance status
    if user.status and user.status.lower() in ['absent', 'present', 'excused', 'late']:
        attendance_record.status = user.status.lower()  # Normalize status to lowercase
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Status can only be 'absent', 'present', 'excused', or 'late'."
        )

    # Step 5: Commit the changes
    db.commit()
    db.refresh(attendance_record)

    # Step 6: Fetch student details for the response
    student = db.query(models.Student).filter(models.Student.id == attendance_record.student_id).first()
    user_info = db.query(models.User).filter(models.User.id == student.user_id).first()

    # Step 7: Return the updated attendance response
    return schemas.AttendanceResponse(
        id=attendance_record.id,
        student_id=student.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        email=user_info.email,
        course_id=attendance_record.course_id,
        attendance_date=attendance_record.attendance_date.date() if attendance_record.attendance_date else date.today(),
        status=attendance_record.status
    )


@router.get('/attendance/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.AttendanceResponse)
def get_attendance_by_student_course(user_id: int, student_id: int, course_id: int, db: Session = Depends(get_db), teacher: bool = Depends(is_teacher)):
    # Step 1: Get the teacher_id based on user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == user_id).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No teacher found with user_id {user_id}."
        )

    # Step 2: Verify if the teacher is assigned to the student and course
    course_assignment = db.query(models.StudentCourse).filter(
        models.StudentCourse.teacher_id == teacher.id,
        models.StudentCourse.student_id == student_id,
        models.StudentCourse.course_id == course_id
    ).first()

    if not course_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with user_id {user_id} (teacher_id {teacher.id}) is not assigned to student {student_id} for course {course_id}."
        )

    # Step 3: Query the attendance record for the student and course
    attendance_record = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.course_id == course_id
    ).first()

    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance record found for student {student_id} in course {course_id}."
        )

    # Step 4: Fetch student details for the response
    student = db.query(models.Student).filter(models.Student.id == attendance_record.student_id).first()
    user_info = db.query(models.User).filter(models.User.id == student.user_id).first()

    # Step 5: Return the fetched attendance response
    return schemas.AttendanceResponse(
        id=attendance_record.id,
        student_id=student.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        email=user_info.email,
        course_id=attendance_record.course_id,
        attendance_date=attendance_record.attendance_date.date() if attendance_record.attendance_date else date.today(),
        status=attendance_record.status
    )