from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_admin
from datetime import date


router = APIRouter(
    prefix="/admin-course",
    tags=['Course']
)   


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Validate if the course already exists
    course_exist = db.query(models.Course).filter(models.Course.course_code == course.course_code).first()
    if course_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Course with code={course.course_code} already exists.")

    # Validate if the teacher exists
    teacher = db.query(models.Teacher).filter(models.Teacher.id == course.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with id={course.teacher_id} does not exist.")
    

    # Create the new course
    new_course = models.Course(**course.dict(exclude_unset=True))
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # Fetch the teacher's personal information
    teacher_personal_data = db.query(models.User).filter(models.User.id == teacher.user_id).first()

    return schemas.CourseResponse(
        id=new_course.id,
        course_name=new_course.course_name,
        course_code=new_course.course_code,
        description=new_course.description,
        teacher=schemas.TeacherInfo(
            id=teacher_personal_data.id,
            first_name=teacher_personal_data.first_name,
            last_name=teacher_personal_data.last_name,
            email=teacher_personal_data.email
        )
    )


@router.get('/{course_id}', status_code=status.HTTP_200_OK, response_model=schemas.CourseResponse)
def get_course_by_id(course_id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Ensure the course is existing
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Course with code={course_id} doesn't exists.")
    
    teacher_personal_data = db.query(models.User).join(
        models.Teacher, models.Teacher.user_id == models.User.id
    ).filter(
        models.Teacher.id == course.teacher_id
    ).first()
    
    if not teacher_personal_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher associated with the course doesn't exist."
        )


    return schemas.CourseResponse(
        id = course.id,
        course_name = course.course_name,
        course_code = course.course_code,
        description = course.description,
        teacher = schemas.TeacherInfo(
            id = teacher_personal_data.id,
            first_name = teacher_personal_data.first_name,
            last_name = teacher_personal_data.last_name,
            email = teacher_personal_data.email
        )
    )


@router.put('/{course_id}', status_code=status.HTTP_200_OK, response_model=schemas.CourseResponse)
def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Fetch the course to be updated
    existing_course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not existing_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with id={course_id} doesn't exist.")


    # If teacher_id is provided, validate the teacher exists
    if course_update.teacher_id:
        teacher = db.query(models.Teacher).filter(models.Teacher.id == course_update.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with id={course_update.teacher_id} does not exist.")


    if course_update.course_code:
        course = db.query(models.Course).filter(models.Course.course_code == course_update.course_code).first()
        if course:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The course with course code={course_update.course_code} already exist.")


    # Update the course with only the provided fields
    course_data = course_update.dict(exclude_unset=True)
    db.query(models.Course).filter(models.Course.id == course_id).update(course_data)
    db.commit()


    # Refresh to get the updated course
    db.refresh(existing_course)

    # Fetch teacher personal data for response
    teacher_personal_data = db.query(models.User).filter(models.User.id == existing_course.teacher.user_id).first()

    # Return the updated course with teacher's information
    return schemas.CourseResponse(
        id=existing_course.id,
        course_name=existing_course.course_name,
        course_code=existing_course.course_code,
        description=existing_course.description,
        teacher=schemas.TeacherInfo(
            id=teacher_personal_data.id,
            first_name=teacher_personal_data.first_name,
            last_name=teacher_personal_data.last_name,
            email=teacher_personal_data.email
        )
    )


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Ensure the course exist
    existing_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not existing_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with id={course_id} doesn't exist.")
    
    # Delete the course
    db.delete(existing_course)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.get('/', status_code=status.HTTP_200_OK, response_model=schemas.ListAllCourses)
def get_all_courses(db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Query for all courses, join with teacher and user to get teacher's user details
    courses = db.query(models.Course, models.User).join(
        models.Teacher, models.Course.teacher_id == models.Teacher.id).join(
            models.User, models.Teacher.user_id == models.User.id).all()
    
    if not courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are no courses in our database.")
    
    # Count total courses
    total = len(courses)

    courses_response = []

    for course, teacher_user in courses:
        courses_response.append(schemas.CourseResponse(
            id=course.id,
            course_name=course.course_name,
            course_code=course.course_code,
            description=course.description,
            teacher=schemas.TeacherInfo(
                id=teacher_user.id,
                first_name=teacher_user.first_name,
                last_name=teacher_user.last_name,
                email=teacher_user.email
            )
        ))
    
    return schemas.ListAllCourses(total=total, courses=courses_response)