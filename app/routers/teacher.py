from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends, Query
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas
from .dependencies import is_teacher, teacher_verify_course, is_admin
from datetime import date

router = APIRouter(
    prefix="/teachers",
    tags=['Teachers']
)


@router.post('/', response_model=schemas.TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Check if the user is already assigned as a teacher
    existing_teacher = db.query(models.Teacher).filter(models.Teacher.user_id == teacher.user_id).first()
    
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="This user is already registered as a teacher."
        )

    # Validate the hire date
    if teacher.hire_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The hire date cannot be in the future."
        )

    if teacher.hire_date < date(1970, 1, 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The hire date cannot be before '1970-01-01'."
        )

    # Create the new teacher
    new_teacher = models.Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return new_teacher


@router.put('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.TeacherResponse)
def update_teacher(id: int, update_validate: schemas.TeacherUpdate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Fetch the existing teacher based on id
    query = db.query(models.Teacher).filter(models.Teacher.id == id)
    existing_user = query.first()

    # If the teacher doesn't exist
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"The Teacher with id={id} does not exist in our database")

    # Validate Department
    if update_validate.department:
        if update_validate.department.isdigit():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"The department cannot accept integers")
    
    # Validate hire_date
    if update_validate.hire_date:
        if update_validate.hire_date < date(1970,1,1) or update_validate.hire_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"The hire date should not be in the future or earlier than 1970")
    
    # Only update provided fields
    if update_validate.hire_date:
        existing_user.hire_date = update_validate.hire_date
    if update_validate.department:
        existing_user.department = update_validate.department

    # Commit the changes and refresh the instance
    db.commit()
    db.refresh(existing_user)

    return existing_user
    

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    # Check if the teacher exists
    existing_user = db.query(models.Teacher).filter(models.Teacher.id == id).first()

    # If the teacher doesn't exist
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The Teacher with id={id} does not exist in our database"
        )

    # Delete the teacher
    db.delete(existing_user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.TeacherResponse])
def get_teachers(db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    display_all_teacher = db.query(models.Teacher).all()

    if not display_all_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"There no teacher assigned in our database"
        )
    
    return display_all_teacher


@router.get('/{id}', status_code=status.HTTP_201_CREATED, response_model=schemas.TeacherResponse)
def get_teachers(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    existing_user = db.query(models.Teacher).filter(models.Teacher.id == id).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The Teacher with id={id} does not exist in our database"
        )
    
    return existing_user



