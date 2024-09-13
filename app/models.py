from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, func, text, ForeignKey, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

# Define classes that carrying tables
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"))

    role = relationship("Role") # that will make live easier bquz we can knowing the role of user


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    enrollment_date = Column(Date, nullable=False)
    current_grade_level = Column(Integer, nullable=False)
    guardian_email = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"))

    user = relationship('User') # for display all personal information


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hire_date = Column(Date, nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'), onupdate=text('NOW()'))

    user = relationship('User') # for display all personal information


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    course_name = Column(String(255), nullable=False)
    course_code = Column(Integer, unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    teacher_id  = Column(Integer, ForeignKey('teachers.id'), nullable=False) 

    teacher = relationship('Teacher')

class StudentCourse(Base):
    __tablename__ = "student_courses"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id  = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    teacher_id  = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    enrollment_date = Column(Date, nullable=False)

    student = relationship('Student')
    course = relationship("Course")
    teacher = relationship("Teacher")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id  = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    attendance_date = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    status = Column(String(20), nullable=False, default='Present')

    student = relationship("Student")
    course = relationship("Course")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id  = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    grade      = Column(String(10), nullable=True)
    comments   = Column(String(255), nullable=True)
    graded_at  = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))

