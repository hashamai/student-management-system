"""Data classes: Course, Enrollment, Student."""
from dataclasses import dataclass, field

from .grading import calculate_gpa, calculate_grade


@dataclass
class Course:
    code: str
    title: str
    credit_hours: int


@dataclass
class Enrollment:
    """A student taking one course in one semester."""
    course: Course
    semester: int
    marks: float | None = None

    @property
    def grade(self):
        return None if self.marks is None else calculate_grade(self.marks)[0]

    @property
    def grade_points(self):
        return None if self.marks is None else calculate_grade(self.marks)[1]


@dataclass
class Student:
    roll_no: str
    name: str
    program: str
    # shortcut: one enrollment per course code, so no retakes; key by (code, semester) if retakes are needed
    enrollments: dict[str, Enrollment] = field(default_factory=dict)

    def enrollment(self, code):
        if code not in self.enrollments:
            raise KeyError(f"{self.name} is not enrolled in {code}")
        return self.enrollments[code]

    def semesters(self):
        return sorted({e.semester for e in self.enrollments.values()})

    def gpa(self, codes):
        return calculate_gpa(self.enrollment(code) for code in codes)

    def semester_gpa(self, semester):
        if semester not in self.semesters():
            raise KeyError(f"{self.name} has no courses in semester {semester}")
        return calculate_gpa(e for e in self.enrollments.values() if e.semester == semester)

    def cgpa(self):
        return calculate_gpa(self.enrollments.values())
