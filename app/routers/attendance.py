from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_teacher, teacher_verify_course
from datetime import date

router = APIRouter(
    prefix="/teachers-attendance",
    tags=['Attendance']
)



@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.AttendanceResponse)
def create_attendance(user: schemas.AttendanceRequest, db: Session = Depends(get_db), teacher_id = Depends(is_teacher)):
    
    # Fetch teacher_id from user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == teacher_id).first()
    
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No teacher found with user_id={teacher_id}")


    # Verify if the teacher is assigned to the student and course
    teacher_verify_course(teacher_id, user.student_id, user.course_id, db)


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



@router.put('/', status_code=status.HTTP_200_OK, response_model=schemas.AttendanceResponse)
def update_attendance(user: schemas.AttendanceRequest, db: Session = Depends(get_db), teacher_id = Depends(is_teacher)):
    # Step 1: Get the teacher_id based on user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == teacher_id).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No teacher found with user_id {teacher_id}."
        )

    # Verify if the teacher is assigned to the student and course
    teacher_verify_course(teacher_id, user.student_id, user.course_id, db)


    # Check if the attendance record exists for this student and course
    attendance_record = db.query(models.Attendance).filter(
        models.Attendance.student_id == user.student_id,
        models.Attendance.course_id == user.course_id
    ).first()

    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record for student {user.student_id} in course {user.course_id} does not exist."
        )

    # Validate and update the attendance status
    if user.status and user.status.lower() in ['absent', 'present', 'excused', 'late']:
        attendance_record.status = user.status.lower()  # Normalize status to lowercase
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Status can only be 'absent', 'present', 'excused', or 'late'."
        )

    #  Commit the changes
    db.commit()
    db.refresh(attendance_record)

    #  Fetch student details for the response
    student = db.query(models.Student).filter(models.Student.id == attendance_record.student_id).first()
    user_info = db.query(models.User).filter(models.User.id == student.user_id).first()

    # Return the updated attendance response
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





@router.get('/{course_id}', status_code=status.HTTP_200_OK, response_model=schemas.ListAttendanceResponse)
def get_attendance_by_course(course_id: int, db: Session = Depends(get_db), teacher_id: int = Depends(is_teacher)):
    # Verify if the teacher is assigned to the course
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == teacher_id).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No teacher found with user_id {teacher_id}."
        )

    # Fetch all attendance records for the specific course, excluding those with status "Present"
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.course_id == course_id,
        models.Attendance.status != "present"  # Exclude "present" records
    ).all()

    if not attendance_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for course {course_id}."
        )


    # Count number of attendance_records for response
    total = len(attendance_records)
    
    # Display the course name for response format
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No course found with course_id {course_id}."
        )
    


    # Fetch student and course details for the response
    response = []
    for record in attendance_records:
        student = db.query(models.Student).filter(models.Student.id == record.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student found with student_id {record.student_id}."
            )
        user_info = db.query(models.User).filter(models.User.id == student.user_id).first()
        response.append(schemas.AttendanceResponse(
            id=record.id,
            student_id=student.id,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            email=user_info.email,
            course_id=record.course_id,
            attendance_date=record.attendance_date.date() if record.attendance_date else date.today(),
            status=record.status
        ))

    # Return the response with total and message
    return schemas.ListAttendanceResponse(
        total=total,
        message=f"Course name: {course.course_name}",
        attendance_records=response
    )