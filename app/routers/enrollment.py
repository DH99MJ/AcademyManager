from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_admin, teacher_verify_course
from datetime import date

router = APIRouter(
    prefix="/admin/enroll-student",
    tags=['Enrollment']
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.EnrollmentResponse)
def enroll_student(enroll: schemas.EnrollmentRequest, db: Session = Depends(get_db), admin_id = Depends(is_admin)):


    # Ensure student already exists
    student = db.query(models.Student).filter(models.Student.id == enroll.student_id).first() 
    if not student:
        raise HTTPException(status_code=404, detail=f"student with id={enroll.student_id} not found")
    # Ensure course already exists
    course = db.query(models.Course).filter(models.Course.id == enroll.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id={enroll.course_id} not found")
    
    # Ensure teacher already exists
    teacher = db.query(models.Teacher).filter(models.Teacher.id == enroll.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id={enroll.teacher_id} not found")

    # Fetch the associated `user_id` of the teacher
    teacher_user_id = teacher.user_id

    # Check if the student is already enrolled in the course with the same teacher
    enrollment_exists = db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == enroll.student_id,
        models.StudentCourse.course_id == enroll.course_id,
        models.StudentCourse.teacher_id == enroll.teacher_id
    ).first()

    if enrollment_exists:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this course with this teacher.")


    if enroll.enrollment_date:
        if enroll.enrollment_date > date.today() or enroll.enrollment_date < date(2000,1,1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The enrollment date should not in the future or older than 2000-1-1")
    
    

    # Create new enrollment
    new_enrollment = models.StudentCourse(
        student_id=enroll.student_id,
        course_id=enroll.course_id,
        teacher_id=enroll.teacher_id,
        enrollment_date=enroll.enrollment_date
    )
    
    # Add new enrollment to the database
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
            first_name=teacher.user.first_name,
            last_name=teacher.user.last_name,
            email=teacher.user.email
        )
    )

# Get enrollments for a specific course
@router.get('/{course_id}', status_code=status.HTTP_200_OK, response_model=schemas.EnrollmentResponseList)
def get_enrollments_by_course(course_id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):
    #  Ensure the course exists and fetch the course name
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id={course_id} not found")
    
    course_name = course.course_name

    #  Fetch all enrollments for the course
    enrollments = db.query(models.StudentCourse).filter(models.StudentCourse.course_id == course_id).all()
    if not enrollments:
        raise HTTPException(status_code=404, detail=f"No enrollments found for course id={course_id}")
    
    #  Prepare the response with enrollment details
    enrollment_responses = []
    for enrollment in enrollments:
        # Fetch student details
        student = db.query(models.Student).filter(models.Student.id == enrollment.student_id).first()
        student_user = db.query(models.User).filter(models.User.id == student.user_id).first()

        # Fetch teacher details
        teacher = db.query(models.Teacher).filter(models.Teacher.id == enrollment.teacher_id).first()
        teacher_user = db.query(models.User).filter(models.User.id == teacher.user_id).first()

        # Build the response for each enrollment, including the course name
        enrollment_responses.append(schemas.EnrollmentResponse(
            message="Enrollment found.",
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            course_name=course_name,  
            teacher_id=enrollment.teacher_id,
            enrollment_date=enrollment.enrollment_date,
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
        ))

    # Step 4: Return the response with total enrollments and the list of records
    return schemas.EnrollmentResponseList(
        total=len(enrollment_responses),
        enrollment_records=enrollment_responses
    )





# # Fetch all enrollments based on course_id
# @router.post('/enroll-student/user_id/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.EnrollmentResponse)
# def enroll_student(enroll: schemas.EnrollmentRequest, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

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