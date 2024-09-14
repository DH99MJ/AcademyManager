from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, Response, HTTPException, status, APIRouter, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .dependencies import is_admin


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreatedResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin_id = Depends(is_admin)):
    
    # hashed password before storing it
    hashed_password = utils.hash_password(user.password_hash)
    user.password_hash = hashed_password

    # Check if already user exist by 'Email'
    user_exist = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Email already registered")

    new_user = models.User(**user.dict())  # Create a new user object from the schema
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.UserCreatedResponse)
def get_user(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The user with id={id} does not exist in our database"
        )

    return user



@router.put('/{id}', response_model=schemas.UserUpdatedResponse)
def update_user(user: schemas.UserUpdate, id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):
    

    # Check if user exist
    user_query = db.query(models.User).filter(models.User.id == id)
    user_to_update = user_query.first()

    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The user with id={id} does not exist in our database"
        )

    if user.email:
        email_duplicate = db.query(models.User).filter(models.User.email == user.email).first()
        if email_duplicate:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The email already exists"
        )


    # Update only the fields provided in the request
    update_data = user.dict(exclude_unset=True)
    user_query.update(update_data, synchronize_session=False)
    db.commit()

    # Return the updated user object
    updated_user = user_query.first()

    return updated_user

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), admin_id = Depends(is_admin)):

    user_query = db.query(models.User).filter(models.User.id == id).first()

    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The user with id={id} does not exist in our database"
        )

    db.delete(user_query)
    db.commit()

    return {"detail": "User deleted successfully"}



