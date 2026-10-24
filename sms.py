"""Simple student management system (command-line)."""

# (minimum marks, letter grade, grade points), highest first
GRADES = [(85, "A", 4.0), (80, "A-", 3.7), (75, "B+", 3.3), (70, "B", 3.0), (65, "B-", 2.7),
          (60, "C+", 2.3), (55, "C", 2.0), (50, "D", 1.0), (0, "F", 0.0)]

# roll_no -> {"name": str, "courses": {code: {"credits": int, "semester": int, "marks": float | None}}}
students = {}


def add_student(roll, name):
    if roll in students:
        raise ValueError(f"Student {roll} already exists")
    students[roll] = {"name": name, "courses": {}}


def add_course(roll, code, credits, semester):
    if credits <= 0:
        raise ValueError("Credit hours must be positive")
    students[roll]["courses"][code] = {"credits": credits, "semester": semester, "marks": None}


def enter_marks(roll, code, marks):
    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100")
    students[roll]["courses"][code]["marks"] = marks


def calculate_grade(marks):
    """Return (letter, grade points) for marks out of 100."""
    for minimum, letter, points in GRADES:
        if marks >= minimum:
            return letter, points


def calculate_gpa(courses):
    """Credit-weighted GPA; courses without marks are ignored."""
    graded = [c for c in courses if c["marks"] is not None]
    credits = sum(c["credits"] for c in graded)
    if not credits:
        return 0.0
    return round(sum(calculate_grade(c["marks"])[1] * c["credits"] for c in graded) / credits, 2)


def semester_gpa(roll, semester):
    return calculate_gpa(c for c in students[roll]["courses"].values() if c["semester"] == semester)


def cgpa(roll):
    return calculate_gpa(students[roll]["courses"].values())


def generate_result(roll):
    student = students[roll]
    lines = [f"Result card: {student['name']} (Roll {roll})"]
    for sem in sorted({c["semester"] for c in student["courses"].values()}):
        lines.append(f"\nSemester {sem}")
        for code, c in student["courses"].items():
            if c["semester"] == sem:
                marks = "-" if c["marks"] is None else c["marks"]
                grade = "-" if c["marks"] is None else calculate_grade(c["marks"])[0]
                lines.append(f"  {code:<10} {c['credits']} cr   marks {marks:<6} grade {grade}")
        lines.append(f"  Semester GPA: {semester_gpa(roll, sem):.2f}")
    lines.append(f"\nCGPA: {cgpa(roll):.2f}")
    return "\n".join(lines)


def show_grade():
    course = students[input("Roll no: ")]["courses"][input("Course code: ")]
    if course["marks"] is None:
        print("Marks not entered yet")
    else:
        print("Grade: %s (%.1f points)" % calculate_grade(course["marks"]))


def show_gpa():
    courses = students[input("Roll no: ")]["courses"]
    codes = input("Course codes (comma separated): ").split(",")
    print("GPA:", calculate_gpa([courses[code.strip()] for code in codes]))


MENU = {
    "1": ("Add student", lambda: add_student(input("Roll no: "), input("Name: "))),
    "2": ("Add course", lambda: add_course(input("Roll no: "), input("Course code: "),
                                           int(input("Credit hours: ")), int(input("Semester: ")))),
    "3": ("Enter marks", lambda: enter_marks(input("Roll no: "), input("Course code: "),
                                             float(input("Marks (0-100): ")))),
    "4": ("Calculate grade", show_grade),
    "5": ("Calculate GPA", show_gpa),
    "6": ("Calculate semester GPA", lambda: print("Semester GPA:", semester_gpa(input("Roll no: "), int(input("Semester: "))))),
    "7": ("Calculate CGPA", lambda: print("CGPA:", cgpa(input("Roll no: ")))),
    "8": ("Generate result", lambda: print(generate_result(input("Roll no: ")))),
}


def main():
    while True:
        print("\n=== Student Management System ===")
        for key, (label, _) in MENU.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            break
        if choice not in MENU:
            print("Invalid choice")
            continue
        try:
            MENU[choice][1]()
        except KeyError as e:
            print("Not found:", e)
        except ValueError as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
