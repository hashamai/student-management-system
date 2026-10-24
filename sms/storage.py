"""Load and save a School as JSON."""
import json

from .school import School


def load(path):
    """Rebuild a School through its normal methods, so file data gets the same validation as user input."""
    school = School()
    if not path.exists():
        return school
    data = json.loads(path.read_text())
    for c in data["courses"]:
        school.add_course(c["code"], c["title"], c["credit_hours"])
    for s in data["students"]:
        school.add_student(s["roll_no"], s["name"], s["program"])
        for e in s["enrollments"]:
            school.enroll(s["roll_no"], e["code"], e["semester"])
            if e.get("marks") is not None:
                school.enter_marks(s["roll_no"], e["code"], e["marks"])
    return school


def save(school, path):
    data = {
        "courses": [vars(c) for c in school.courses.values()],
        "students": [
            {"roll_no": s.roll_no, "name": s.name, "program": s.program,
             "enrollments": [{"code": code, "semester": e.semester, "marks": e.marks}
                             for code, e in s.enrollments.items()]}
            for s in school.students.values()
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)  # atomic swap: a crash mid-write never corrupts the saved data
