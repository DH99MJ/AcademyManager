
# **AcademyManager**
AcademyManager is a comprehensive Student Information System (SIS) designed to streamline academic operations in educational institutions. Built with FastAPI and PostgreSQL, it allows flexible management of student enrollment, course tracking, attendance, and grading. The system is designed to be scalable and adaptable to various institutional needs.

# **Key Features**
- **Student Enrollment**: Manage student enrollments in courses, including assigning teachers and tracking course registrations.
- **Course Management**: Create, update, and delete courses. Teachers are assigned specific courses, and students can be enrolled in those courses.
- **Attendance Tracking**: Teachers can create, update, and track attendance for students, including marking students as 'Present', 'Absent', 'Excused', or 'Late'.
- **Grade Management**: Teachers can manage grades for their assigned students, allowing students to view their grades and performance across different courses.
- **Student Portal**: Students can view their attendance, course enrollments, and grades through a dedicated interface.

# **API Endpoints**
Here is a description of all the available routes in the FastAPI system:

**User Routes**
- **POST /users/** - Create a new user [Admin].
- **GET /users/{id}** - Get user details by ID [Admin].
- **PUT /users/{id}** - Update a user by ID [Admin].
- **DELETE /users/{id}** - Delete a user by ID [Admin].

**Student Routes**
- **POST /students/** - Create a new student [Admin].
- **GET /students/** - Get all students [Admin].
- **GET /students/{id}** - Get student details by ID [Admin].
- **PUT /students/{id}** - Update student information by ID [Admin].
- **DELETE /students/{id}** - Delete a student by ID [Admin].

**Teacher Routes**
- **POST /teachers/** - Create a new teacher [Admin].
- **GET /teachers/** - Get all teachers [Admin].
- **GET /teachers/{id}** - Get teacher details by ID [Admin].
- **PUT /teachers/{id}** - Update teacher details by ID [Admin].
- **DELETE /teachers/{id}** - Delete a teacher by ID [Admin].

**Attendance Routes**
- **POST /teachers-attendance/** - Create attendance for a student [Teacher].
- **PUT /teachers-attendance/** - Update attendance records [Teacher].
- **GET /teachers-attendance/{course_id}** - Get all attendance records by course [Teacher].

**Course Routes**
- **POST /admin-course/** - Create a new course [Admin].
- **GET /admin-course/** - Get all courses [Admin].
- **GET /admin-course/{course_id}** - Get course details by ID [Admin].
- **PUT /admin-course/{course_id}** - Update course details by ID [Admin].
- **DELETE /admin-course/{course_id}** - Delete a course by ID [Admin].

**Enrollment Routes**
- **POST /admin/enroll-student/** - Enroll a student in a course [Admin].
- **GET /admin/enroll-student/{course_id}** - Get enrollments by course ID [Admin].

**Grade Routes**
- **POST /teacher-grades/** - Create a grade for a student [Teacher].
- **PUT /teacher-grades/{grade_id}** - Update a student's grade [Teacher].
- **DELETE /teacher-grades/{grade_id}** - Delete a student's grade [Teacher].

**Authentication Routes**
- **POST /Login/** - User login to get access tokens [Admin, Teacher, and Student].

**Student Attendance & Grades Routes**
- **GET /student-attendance/** - Get a student's attendance [Student].
- **GET /student-grades/** - Get a student's grades [Student].

**Technologies Used**
- Backend Framework: FastAPI
- Database: PostgreSQL
- Authentication: OAuth2 (planned for secure login and role-based access control)
- ORM: SQLAlchemy
- Database Migrations: Alembic

**Installation**
Clone the repository:

```
git clone https://github.com/your-username/AcademyManager.git
```

Navigate to the project directory:

```
cd AcademyManager
```

Install the dependencies:

```
pip install -r requirements.txt
```

Create a .env file for your environment variables:

```
touch .env
```

Add your database credentials, secret keys, and other sensitive configurations inside the .env file:

```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432  
DB_NAME=sis_fastapi
```

Run the migrations to set up the database:

```
alembic upgrade head
```

Start the FastAPI server:

```
uvicorn app.main:app --reload
```

**Setting Up Initial Data**
After cloning the project, you’ll need to set up the initial roles and users for the system to function correctly:

1. **Insert Roles into the roles Table**
You need to insert the following roles into the roles table first:

```
INSERT INTO roles (id, role_name) VALUES (1, 'Admin');
INSERT INTO roles (id, role_name) VALUES (2, 'Teacher');
INSERT INTO roles (id, role_name) VALUES (3, 'Student');
```

2. **Hash the Password**
Since passwords are hashed, you need to hash any passwords before inserting users into the database. Use the project’s utility to generate a hashed password:

```python
from app.utils import hash_password
hashed_password = hash_password("your_plain_password")
print(hashed_password)
```

3. **Insert Users**
After generating the hashed password, you can insert users into the database:

```
INSERT INTO users (email, password_hash, first_name, last_name, role_id) 
VALUES ('admin@example.com', 'your_hashed_password_here', 'Admin', 'User', 1);
```

For Teachers, use role_id = 2, and for Students, use role_id = 3.

**Usage**
- Teachers can log in to manage student attendance, grades, and course enrollments.
- Students can log in to view their academic progress, including attendance and grades.

**Future Improvements**
- Create a responsive frontend for a better user experience.
