from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from ..oauth2 import get_current_user





def teacher_verify_course(user_id: int, student_id: int, course_id: int, db: Session = Depends(get_db)):
    #  Get the teacher_id based on user_id
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == user_id).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No teacher found with user_id {user_id}."
        )

    #  Verify if the teacher is assigned to the student and course
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

    return True

# Ensure that who makes Create, update, delete is teacher!
def is_teacher(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)) -> int:

    print(f"Checking teacher permissions for user with ID {current_user.id} and role ID {current_user.role_id}")

    # Ensure the current user exists and has teacher privileges (teacher role_id = 2)
    if current_user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"User id={current_user.id} does not have teacher permissions"
        )
    
    # Return the teacher's user_id
    return current_user.id


# Function that ensures modifications are done by an admin
def is_admin(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)) -> int:
    print(f"Checking admin permissions for user with ID {current_user.id} and role ID {current_user.role_id}")

    # Ensure the current user exists and has admin privileges (Admin role_id = 1)
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"User id={current_user.id} does not have admin permissions"
        )
    
    # Return the admin's user_id
    return current_user.id



def is_student(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)) -> int:
    
    print(f"Checking student permissions for user with ID {current_user.id} and role ID {current_user.role_id}")

    # Ensure the current user exists and has student privileges (Student role_id = 3)
    if current_user.role_id != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"User id={current_user.id} does not have student permissions"
        )
    
    # Return the student's user_id
    return current_user.id