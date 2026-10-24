import tempfile
from pathlib import Path

from sms import storage
from sms.grading import calculate_grade
from sms.report import result_card
from sms.school import School

SAMPLE_FILE = Path(__file__).parent / "data" / "sample_data.json"


def make_school():
    school = School()
    school.add_course("CS101", "Programming", 3)
    school.add_course("MA101", "Calculus", 2)
    school.add_course("CS201", "Data Structures", 4)
    school.add_student("1", "Ali", "BSCS")
    for code, semester, marks in [("CS101", 1, 90), ("MA101", 1, 72), ("CS201", 2, 49)]:
        school.enroll("1", code, semester)
        school.enter_marks("1", code, marks)
    return school


def test_grades_and_gpa():
    student = make_school().student("1")
    assert calculate_grade(85) == ("A", 4.0)
    assert calculate_grade(49.9) == ("F", 0.0)
    assert student.semester_gpa(1) == 3.6         # (4*3 + 3*2) / 5
    assert student.semester_gpa(2) == 0.0
    assert student.gpa(["CS101", "CS201"]) == 1.71  # 12 / 7
    assert student.cgpa() == 2.0                  # 18 / 9
    assert "CGPA: 2.00" in result_card(student)


def test_validation():
    school = make_school()
    for bad in (lambda: school.add_student("1", "Dup", "BSCS"),
                lambda: school.add_course("X1", "Bad", 0),
                lambda: school.enroll("1", "CS101", 1),        # already enrolled
                lambda: school.enroll("1", "NOPE", 1),         # unknown course
                lambda: school.enter_marks("1", "CS101", 101),
                lambda: school.enter_marks("2", "CS101", 50),  # unknown student
                lambda: school.student("1").semester_gpa(5)):
        try:
            bad()
            assert False, "expected an error"
        except (KeyError, ValueError):
            pass


def test_storage_round_trip():
    school = storage.load(SAMPLE_FILE)
    assert len(school.students) == 7 and len(school.courses) == 10
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "school.json"
        storage.save(school, path)
        reloaded = storage.load(path)
    assert {r: s.cgpa() for r, s in reloaded.students.items()} == {r: s.cgpa() for r, s in school.students.items()}


if __name__ == "__main__":
    test_grades_and_gpa()
    test_validation()
    test_storage_round_trip()
    print("All tests passed")
