from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, schemas, models, utils, oauth2
from ..database import get_db


router = APIRouter(
    tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Fetch the user based on provided username (which is 'email')
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )


    # Verify password using the utils.verify_password function
    if not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    

    # Generate a token if credntials are correct
    access_token = oauth2.create_access_token(data={"user_id": user.id, "role_id": user.role_id})

    # Return the token in reponse
    return {"access_token": access_token, "token_type": "bearer"}

