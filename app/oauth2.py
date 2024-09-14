from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
# OAuth2PasswordBearer provides a URL for obtaining a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# .env file
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


# Function to create an access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode the JWT token with secret and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify access token
def verify_access_token(token: str, credentials_exception):
    try:
        # Remove "Bearer " prefix if it exists
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = str(payload.get('user_id'))
        role_id: str = str(payload.get('role_id'))

        if user_id is None or role_id is None:
            raise credentials_exception
        
        # Return token data (user_id, role_id)
        return schemas.TokenData(id=user_id, role_id=role_id)

    except JWTError:
        raise credentials_exception

# Function to fetch the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Verify the access token
    return verify_access_token(token, credentials_exception)