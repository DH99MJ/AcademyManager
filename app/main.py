from fastapi import FastAPI, APIRouter
from . import models
from .database import engine
from .routers import user, student, teacher, attendance, course, enrollment, grade, oauth, student_routes, grades_routes

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()



app.include_router(user.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(attendance.router)
app.include_router(course.router)
app.include_router(enrollment.router)
app.include_router(grade.router)
app.include_router(oauth.router)
app.include_router(student_routes.router)
app.include_router(grades_routes.router)





@app.get("/")
def root():
    return {"message": "Database tables created successfully!"}