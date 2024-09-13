from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models




# Check if the teacher is assigned to the course with the student
# def teacher_verify_course(teacher_id: int, student_id: int , course_id: int, db: Session = Depends(get_db)):
#     course_assignment = db.query(models.StudentCourse).filter(
#         models.StudentCourse.course_id == course_id,              
#         models.StudentCourse.teacher_id == teacher_id,              
#         models.StudentCourse.student_id == student_id               
#     ).first()

#     if not course_assignment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"Teacher {teacher_id} is not assigned to student {student_id} for course {course_id}"
#         )
    

def teacher_verify_course(teacher_id: int, student_id: int, course_id: int, db: Session = Depends(get_db)):
    # Ensure all parameters are valid
    if not teacher_id or not student_id or not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Teacher ID, Student ID, and Course ID must be provided"
        )
    
    # Check if the student is enrolled in the course with the specified teacher
    course_assignment = db.query(models.StudentCourse).filter(
        models.StudentCourse.course_id == course_id,
        models.StudentCourse.teacher_id == teacher_id,
        models.StudentCourse.student_id == student_id
    ).first()

    # If no assignment is found, raise an error
    if not course_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher {teacher_id} is not assigned to student {student_id} for course {course_id}"
        )
    
    return True



# Ensure that who makes Create, update, delete is teacher!
def is_teacher(user_id: int, db: Session = Depends(get_db)) -> int:

    # Fetch user with the given user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User associated with this id={user_id} does not exist"
        )
    
    # Ensure the user is a teacher (role_id == 2)
    if user.role_id != 2: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"The user id={user_id} doesn't have the permissions to access"
        )
    
    # Return only the user id (integer)
    return user.id

# Function that ensures modifications are done by an admin
def is_admin(user_id: int, db: Session = Depends(get_db)) -> models.User:

    # Fetch user
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User associated with this id={user_id} does not exist"
        )

    # Ensure the user is an admin (Admin role_id = 1)
    if user.role_id != 1:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"The user id={user_id} doesn't have admin permissions"
        )
    
    return user.id



def is_student(user_id: int, db: Session = Depends(get_db)) -> int:
    
    # Fetch user
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id={user_id} does not exist"
        )

    # Ensure the user is a student (role_id = 3)
    if user.role_id != 3:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"The user id={user_id} doesn't have student permissions"
        )
    
    return user.id  # Return only the user ID as before