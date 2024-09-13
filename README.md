# AcademyManager

**AcademyManager** is a comprehensive Student Information System (SIS) designed to streamline academic operations in educational institutions. Built with FastAPI and PostgreSQL, it allows flexible management of student enrollment, course tracking, attendance, and grading. The system is designed to be scalable and adaptable to various institutional needs.

## Key Features

- **Student Enrollment**: Manage student enrollments in courses, including assigning teachers and tracking course registrations.
  
- **Course Management**: Create, update, and delete courses. Teachers are assigned specific courses, and students can be enrolled in those courses.

- **Attendance Tracking**: Teachers can create, update, and track attendance for students, including marking students as 'Present', 'Absent', 'Excused', or 'Late'.

- **Grade Management**: Teachers can manage grades for their assigned students, allowing students to view their grades and performance across different courses.

- **Student Portal**: Students can view their attendance, course enrollments, and grades through a dedicated interface.

## API Endpoints

- **Teacher Endpoints**:
  - Manage course enrollments, create, update, and delete attendance records.
  - Grade students and track performance.

- **Student Endpoints**:
  - View attendance and grade details.
  - See assigned courses and performance in the courses.

## Technologies Used

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: OAuth2 (Planned for secure login and role-based access control)
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/AcademyManager.git

2.	Navigate to the project directory:
    - cd AcademyManager
  	
3.	Install the dependencies:
     - pip install -r requirements.txt

4.	Create a .env file for your environment variables:
     - touch .env
     - Add your database credentials, secret keys, and other sensitive configurations inside the .env file.

5.	Run the migrations to set up the database:
    - alembic upgrade head

6.	Start the FastAPI server:
    - uvicorn app.main:app --reload


Usage

	•	Teachers can log in to manage student attendance, grades, and course enrollments.
	•	Students can log in to view their academic progress, including attendance and grades.

Future Improvements

	•	Implement OAuth2 for secure authentication and role-based access control.
	•	Add more advanced features for academic performance tracking and reporting.
	•	Create a responsive frontend for a better user experience.
