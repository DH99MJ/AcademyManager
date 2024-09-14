from typing import List
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import date
from .dependencies import is_student

router = APIRouter(
    prefix='/student-attendance',
    tags=['Student Attendance']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model=schemas.ListStudentAttendanceResponse)
def get_student_attendance(db: Session = Depends(get_db), student_id: int = Depends(is_student)):
    # Fetch the attendance records for the student
    attendance_records = db.query(
        models.Attendance, 
        models.Course.course_name
    ).join(
        models.Course, models.Course.id == models.Attendance.course_id
    ).filter(
        models.Attendance.student_id == student_id
    ).all()

    if not attendance_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for student {student_id}"
        )

    # Format the response
    attendance_list = [
        schemas.StudentAttendanceResponse(
            id=attendance.id,
            course_name=course_name,
            attendance_date=attendance.attendance_date.date() if attendance.attendance_date else date.today(),
            status=attendance.status
        )
        for attendance, course_name in attendance_records
    ]

    return schemas.ListStudentAttendanceResponse(attendance_records=attendance_list)