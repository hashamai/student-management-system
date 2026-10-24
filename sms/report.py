"""Printable reports."""


def result_card(student):
    lines = [f"Result card: {student.name} (Roll {student.roll_no}, {student.program})"]
    for sem in student.semesters():
        lines.append(f"\nSemester {sem}")
        for e in student.enrollments.values():
            if e.semester == sem:
                marks = "-" if e.marks is None else e.marks
                lines.append(f"  {e.course.code:<7}{e.course.title:<40}{e.course.credit_hours} cr"
                             f"   marks {marks:<6} grade {e.grade or '-'}")
        lines.append(f"  Semester GPA: {student.semester_gpa(sem):.2f}")
    lines.append(f"\nCGPA: {student.cgpa():.2f}")
    return "\n".join(lines)


def student_list(school):
    """All students, highest CGPA first."""
    lines = [f"{'Roll no':<10}{'Name':<20}{'Program':<9}CGPA"]
    for s in sorted(school.students.values(), key=lambda s: s.cgpa(), reverse=True):
        lines.append(f"{s.roll_no:<10}{s.name:<20}{s.program:<9}{s.cgpa():.2f}")
    return "\n".join(lines)


def course_list(school):
    lines = [f"{'Code':<8}{'Title':<40}Credits"]
    lines += [f"{c.code:<8}{c.title:<40}{c.credit_hours}" for c in school.courses.values()]
    return "\n".join(lines)
