"""Student Management System - command-line menu. Run: python3 main.py"""
from pathlib import Path

from sms import storage
from sms.report import course_list, result_card, student_list

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "school.json"          # your saved data (created on first change)
SAMPLE_FILE = DATA_DIR / "sample_data.json"   # starting data, never overwritten


def ask(prompt):
    return input(prompt).strip()


def ask_roll():
    return ask("Roll no: ").upper()


def ask_code():
    return ask("Course code: ").upper()


def add_student(school):
    school.add_student(ask_roll(), ask("Name: "), ask("Program (e.g. BSCS): ").upper())


def add_course(school):
    school.add_course(ask_code(), ask("Title: "), int(ask("Credit hours: ")))


def enroll(school):
    school.enroll(ask_roll(), ask_code(), int(ask("Semester: ")))


def enter_marks(school):
    school.enter_marks(ask_roll(), ask_code(), float(ask("Marks (0-100): ")))


def show_grade(school):
    e = school.student(ask_roll()).enrollment(ask_code())
    print("Marks not entered yet" if e.marks is None else f"Grade: {e.grade} ({e.grade_points} points)")


def show_gpa(school):
    student = school.student(ask_roll())
    codes = ask("Course codes (comma separated): ").upper().split(",")
    print("GPA:", student.gpa(code.strip() for code in codes))


def show_semester_gpa(school):
    student = school.student(ask_roll())
    print("Semester GPA:", student.semester_gpa(int(ask("Semester: "))))


def show_cgpa(school):
    print("CGPA:", school.student(ask_roll()).cgpa())


def show_result(school):
    print(result_card(school.student(ask_roll())))


MENU = {
    "1": ("Add student", add_student),
    "2": ("Add course", add_course),
    "3": ("Enroll student in course", enroll),
    "4": ("Enter marks", enter_marks),
    "5": ("Calculate grade", show_grade),
    "6": ("Calculate GPA", show_gpa),
    "7": ("Calculate semester GPA", show_semester_gpa),
    "8": ("Calculate CGPA", show_cgpa),
    "9": ("Generate result", show_result),
    "10": ("List students", lambda school: print(student_list(school))),
    "11": ("List courses", lambda school: print(course_list(school))),
}


def main():
    school = storage.load(DATA_FILE if DATA_FILE.exists() else SAMPLE_FILE)
    while True:
        print("\n=== Student Management System ===")
        for key, (label, _) in MENU.items():
            print(f"{key:>2}. {label}")
        print(" 0. Exit")
        choice = ask("Choose: ")
        if choice == "0":
            break
        if choice not in MENU:
            print("Invalid choice")
            continue
        try:
            MENU[choice][1](school)
        except (KeyError, ValueError) as e:
            print("Error:", e.args[0])
            continue
        storage.save(school, DATA_FILE)  # save after every action so nothing is lost on exit or crash


if __name__ == "__main__":
    main()
