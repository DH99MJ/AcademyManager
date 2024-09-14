from typing import List
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import date
from .dependencies import is_student, is_admin

router = APIRouter(
    prefix='/students',
    tags=['Students']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Check if the user exists based on guardian email
    user = db.query(models.User).filter(models.User.email == student.guardian_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User associated with this email does not exist"
        )
    
    # Check if a student with the same guardian email already exists
    std_exist = db.query(models.Student).filter(models.Student.guardian_email == student.guardian_email).first()
    if std_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="A student with this guardian email already exists"
        )
    
    # Create the new student using the fetched user_id, created_at will be automatically set by the database
    new_student = models.Student(user_id=user.id, **student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# @router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.StudentResponse)
# def get_student(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

#     # Check if student exist
#     std_exist = db.query(models.Student).filter(models.Student.id == id).first()
#     if not std_exist:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"The student with id={id} does not exist in our database"
#         )

#     return std_exist



@router.get('/{id}', status_code=status.HTTP_201_CREATED, response_model=schemas.StudentResponse)
def get_student(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    existing_user = db.query(models.Student).filter(models.Student.id == id).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The Student with id={id} does not exist in our database"
        )
    
    return existing_user


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Query that check if user exists based on id
    delete_query = db.query(models.Student).filter(models.Student.id == id)

    # Check if user doesn't exists
    if not delete_query.first():   
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The student with id={id} does not exist in our database"
        )
    
    delete_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put('/{id}', response_model=schemas.StudentUpdatedResponse)
def update_student(student: schemas.StudentUpdate, id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):
    
    # Get the existing student record
    std_exist = db.query(models.Student).filter(models.Student.id == id)

    student_data = std_exist.first()

    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"The student with id={id} does not exist in our database")


    # Validate for all dates
    if student.date_of_birth: # Provided in request
        if student.date_of_birth > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The date of birth should not in the future")

    if student.enrollment_date:
        if student.enrollment_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The enrollment date should not in the future")
    
    if student.enrollment_date and student.date_of_birth:
        if student.enrollment_date < student.date_of_birth:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The the date of birth should not greater than enrollment")

    # This part will ensure the age is makes sense
    if student.enrollment_date and student.date_of_birth:
        today = date.today()
        current_age = today.year - student.date_of_birth.year - ((today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day))
        
        if current_age < 17:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The student is too young for this grade level.")
        
        elif current_age > 25:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The student age should not greater than 25.")
    

    # If guardian_email is provided, ensure the associated user exists
    if student.guardian_email:
        user = db.query(models.User).filter(models.User.email == student.guardian_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User associated with this email does not exist"
            )
        student_data.user_id = user.id  # Update the user_id if the guardian email changes

    # Update only the fields provided
    std_exist.update(student.dict(exclude_unset=True), synchronize_session=False)
    db.commit()

    db.refresh(student_data)  # Refresh to get the updated student data, including updated_at

    return student_data

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    display_all_student = db.query(models.Student).all()

    if not display_all_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There no student in our database"
        )
    
    return display_all_student


# @router.get('/grades/user_id/{user_id}', response_model=List[schemas.ResponseGrade])
# def get_own_grades(user_id: int, db: Session = Depends(get_db), student_id = Depends(is_student) ):

#     # Fetch grades and course information for the specific student
#     grades = db.query(
#         models.Grade.id,
#         models.Grade.student_id,
#         models.Grade.course_id,
#         models.Grade.grade,
#         models.Grade.comments,
#         models.Grade.graded_at,
#         models.Course.course_name  # Fetch course_name from the Course table
#     ).join(
#         models.Course, models.Course.id == models.Grade.course_id  # Join with the Course table
#     ).filter(
#         models.Grade.student_id == user_id
#     ).all()

#     # Check if any grades are returned
#     if not grades:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No grades found for the student")

#     # Map to ResponseGrade schema
#     return [
#         schemas.ResponseGrade(
#             id=grade.id,
#             student_id=grade.student_id,
#             course_id=grade.course_id,
#             course_name=grade.course_name,
#             grade=grade.grade,
#             comments=grade.comments,
#             graded_at=grade.graded_at.date()
#         )
#         for grade in grades
#     ]





# @router.get('/attendance/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.ListStudentAttendanceResponse)
# def get_student_attendance(user_id: int, db: Session = Depends(get_db), student: bool = Depends(is_student)):
#     # Fetch the student record using user_id
#     student_record = db.query(models.Student).filter(models.Student.user_id == user_id).first()

#     if not student_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No student found with user_id {user_id}"
#         )   

#     # Fetch the attendance records for the student
#     attendance_records = db.query(
#         models.Attendance, 
#         models.Course.course_name
#     ).join(
#         models.Course, models.Course.id == models.Attendance.course_id
#     ).filter(
#         models.Attendance.student_id == student_record.id
#     ).all()

#     if not attendance_records:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No attendance records found for student {student_record.id}"
#         )

#     # Format the response
#     attendance_list = [
#         schemas.StudentAttendanceResponse(
#             id=attendance.id,
#             course_name=course_name,
#             attendance_date=attendance.attendance_date.date() if attendance.attendance_date else date.today(),
#             status=attendance.status
#         )
#         for attendance, course_name in attendance_records
#     ]

#     return schemas.ListStudentAttendanceResponse(attendance_records=attendance_list)


