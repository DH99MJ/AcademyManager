from pydantic import BaseModel, EmailStr, conint
from typing import List, Optional
from datetime import datetime, date

# Schemas for creating a new user
class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role_id: int

# Schemas for updating an existing user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None

class UserCreatedResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True
 

class UserUpdatedResponse(UserCreatedResponse):
    updated_at: datetime

    class Config:
        from_attributes = True

# Schemas for the related User
class UserInStudentResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    date_of_birth: date
    enrollment_date: date
    current_grade_level: conint(ge=1, le=10)  # Restricted the level values between 1 and 10
    guardian_email: EmailStr

class StudentUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    enrollment_date: Optional[date] = None
    current_grade_level: Optional[conint(ge=1, le=10)] = None # Restricted the level values between 1 and 10
    guardian_email: EmailStr
    

class StudentResponse(BaseModel):
    id: int
    user: UserInStudentResponse
    date_of_birth: date
    enrollment_date: date
    current_grade_level: int
    created_at: datetime
    # Personal information extra feilds for clarification.
    
    class Config:
        from_attributes = True

class StudentUpdatedResponse(StudentResponse):
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateGrade(BaseModel):
    student_id: int
    course_id: int 
    grade: str
    comments: str

class ResponseGrade(CreateGrade):
    id: int
    graded_at: date

    class Config:
        from_attributes = True 

class ResponseGradeForStudent(BaseModel):
    id: int
    student_id: int
    course_id: int
    course_name: str  
    grade: str
    comments: str
    graded_at: date

    class Config:
        from_attributes = True


class UpdateGrade(BaseModel):
    grade: Optional[str] = None
    comments: Optional[str] = None

class TeacherCreate(BaseModel):
    user_id: int
    hire_date: date
    department: str

class TeacherResponse(BaseModel):
    id: int
    user_id: int
    hire_date: date
    department: str
    user: UserInStudentResponse  # Nested user information (id, first_name, last_name, email)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
class TeacherUpdate(BaseModel):
    hire_date: Optional[date] = None
    department: Optional[str] = None  

    class Config:
        from_attributes = True
    

class AttendanceRequest(BaseModel):
    student_id: int
    course_id: int
    status: Optional[str] = "Present" # By default all students present

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    first_name: str
    last_name: str
    email: EmailStr
    course_id: int
    attendance_date: date
    status: str

    class Config:
        from_attributes = True

class SimpleAttendanceResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    attendance_date: date
    status: str

    class Config:
        from_attributes = True


class GetAttendanceResponse(BaseModel):
    id: int
    student_id: int
    first_name: str
    last_name: str
    email: EmailStr
    course_name: str  # Add the course name
    attendance_date: date
    status: str

    class Config:
        from_attributes = True

class TeacherInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    course_name: str
    course_code: int
    description: Optional[str] = None
    teacher_id: int

class CourseResponse(BaseModel):
    id: int
    course_name: str
    course_code: int
    description: Optional[str] = None
    teacher: TeacherInfo

    class Config:
        from_attributes = True


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    course_code: Optional[int] = None
    description: Optional[str] = None
    teacher_id:  Optional[int] = None


class ListAllCourses(BaseModel):
    total: int
    courses: List[CourseResponse]


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class EnrollmentRequest(BaseModel):
    student_id: int
    course_id: int
    teacher_id: int
    enrollment_date: date

class EnrollmentResponse(BaseModel):
    message: str
    student_id: int
    course_id: int
    teacher_id: int
    enrollment_date: date
    student_info: PersonalInfo
    teacher_info: PersonalInfo



class StudentAttendanceResponse(BaseModel):
    id: int
    course_name: str
    attendance_date: date
    status: str


class ListStudentAttendanceResponse(BaseModel):
    attendance_records: List[StudentAttendanceResponse]