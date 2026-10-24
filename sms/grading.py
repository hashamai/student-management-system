"""Grading scale and GPA maths."""

# (minimum marks, letter grade, grade points), highest first
GRADES = [(85, "A", 4.0), (80, "A-", 3.7), (75, "B+", 3.3), (70, "B", 3.0), (65, "B-", 2.7),
          (60, "C+", 2.3), (55, "C", 2.0), (50, "D", 1.0), (0, "F", 0.0)]


def calculate_grade(marks):
    """Return (letter, grade points) for marks out of 100."""
    for minimum, letter, points in GRADES:
        if marks >= minimum:
            return letter, points


def calculate_gpa(enrollments):
    """Credit-weighted GPA; enrollments without marks are ignored."""
    graded = [e for e in enrollments if e.marks is not None]
    credits = sum(e.course.credit_hours for e in graded)
    if not credits:
        return 0.0
    return round(sum(e.grade_points * e.course.credit_hours for e in graded) / credits, 2)
