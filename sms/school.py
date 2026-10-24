"""School: owns all students and courses; every change goes through here and is validated."""
from .models import Course, Enrollment, Student


class School:
    def __init__(self):
        self.students = {}  # roll no -> Student
        self.courses = {}   # course code -> Course

    def add_student(self, roll_no, name, program):
        if not roll_no or not name:
            raise ValueError("Roll no and name are required")
        if roll_no in self.students:
            raise ValueError(f"Student {roll_no} already exists")
        self.students[roll_no] = Student(roll_no, name, program)

    def add_course(self, code, title, credit_hours):
        if not code or not title:
            raise ValueError("Course code and title are required")
        if code in self.courses:
            raise ValueError(f"Course {code} already exists")
        if credit_hours <= 0:
            raise ValueError("Credit hours must be positive")
        self.courses[code] = Course(code, title, credit_hours)

    def enroll(self, roll_no, code, semester):
        student, course = self.student(roll_no), self.course(code)
        if code in student.enrollments:
            raise ValueError(f"{student.name} is already enrolled in {code}")
        if semester < 1:
            raise ValueError("Semester must be 1 or more")
        student.enrollments[code] = Enrollment(course, semester)

    def enter_marks(self, roll_no, code, marks):
        if not 0 <= marks <= 100:
            raise ValueError("Marks must be between 0 and 100")
        self.student(roll_no).enrollment(code).marks = marks

    def student(self, roll_no):
        if roll_no not in self.students:
            raise KeyError(f"No student with roll no {roll_no}")
        return self.students[roll_no]

    def course(self, code):
        if code not in self.courses:
            raise KeyError(f"No course with code {code}")
        return self.courses[code]
