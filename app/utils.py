from passlib.context import CryptContext

# Use bcrypt algorithm for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

# Function to hash a plain-text password
def hash_password(password: str):
    return pwd_context.hash(password)

# Function to verify a plain-text password against a hashed password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)