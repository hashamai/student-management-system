"""Student Management System - desktop UI (Tkinter). Run: python3 gui.py"""
import tkinter as tk
from tkinter import messagebox, ttk

from main import DATA_FILE, SAMPLE_FILE
from sms import storage
from sms.report import result_card


def table(parent, columns, **options):
    """A Treeview with headed columns; columns maps heading -> width."""
    tree = ttk.Treeview(parent, columns=list(columns), show="headings", **options)
    for name, width in columns.items():
        tree.heading(name, text=name)
        tree.column(name, width=width, anchor="w")
    return tree


def fill(tree, rows):
    """Replace all rows (the first value is the row id), keeping the selection."""
    selected = tree.selection()
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", iid=row[0], values=row)
    tree.selection_set([i for i in selected if tree.exists(i)])


def form(parent, labels):
    """Labelled entries stacked in a grid; returns their StringVars."""
    variables = []
    for row, label in enumerate(labels):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=2)
        variables.append(var)
    parent.columnconfigure(1, weight=1)
    return variables


def number(var, convert, label):
    try:
        return convert(var.get().strip())
    except ValueError:
        raise ValueError(f"{label} must be a number") from None


class App(tk.Tk):
    def __init__(self, data_file=DATA_FILE):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1150x620")
        ttk.Style(self).theme_use("clam")
        self.data_file = data_file
        self.school = storage.load(data_file if data_file.exists() else SAMPLE_FILE)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=8, pady=8)
        tabs.add(self.build_students_tab(tabs), text="Students")
        tabs.add(self.build_courses_tab(tabs), text="Courses")
        self.refresh()

    # ---------- layout ----------

    def build_students_tab(self, parent):
        tab = ttk.Frame(parent, padding=8)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        students = ttk.LabelFrame(tab, text="Students (ranked by CGPA)", padding=8)
        students.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.students_tree = table(students, {"Roll no": 80, "Name": 140, "Program": 70, "CGPA": 60})
        self.students_tree.pack(fill="both", expand=True)
        self.students_tree.bind("<<TreeviewSelect>>", lambda _: self.show_student())

        add = ttk.LabelFrame(tab, text="Add student", padding=8)
        add.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(8, 0))
        student_vars = form(add, ["Roll no", "Name", "Program"])
        ttk.Button(add, text="Add student", command=lambda: self.add_student(*student_vars)).grid(
            row=3, column=1, sticky="e", pady=(4, 0))

        self.detail = ttk.LabelFrame(tab, padding=8)
        self.detail.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.enroll_tree = table(self.detail, {"Code": 70, "Title": 300, "Credits": 60, "Semester": 70,
                                               "Marks": 60, "Grade": 60}, selectmode="extended")
        self.enroll_tree.pack(fill="both", expand=True)
        self.enroll_tree.bind("<<TreeviewSelect>>", lambda _: self.show_selection())
        self.summary = ttk.Label(self.detail)
        self.summary.pack(anchor="w", pady=(8, 0))
        self.selection_info = ttk.Label(self.detail)
        self.selection_info.pack(anchor="w", pady=(4, 0))

        actions = ttk.Frame(self.detail)
        actions.pack(fill="x", pady=(8, 0))
        self.course_var, self.semester_var, self.marks_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        ttk.Label(actions, text="Course").pack(side="left")
        self.course_box = ttk.Combobox(actions, textvariable=self.course_var, state="readonly", width=8)
        self.course_box.pack(side="left", padx=(4, 8))
        ttk.Label(actions, text="Semester").pack(side="left")
        ttk.Entry(actions, textvariable=self.semester_var, width=4).pack(side="left", padx=4)
        ttk.Button(actions, text="Enroll", command=self.enroll).pack(side="left", padx=(0, 24))
        ttk.Label(actions, text="Marks").pack(side="left")
        ttk.Entry(actions, textvariable=self.marks_var, width=6).pack(side="left", padx=4)
        ttk.Button(actions, text="Save marks", command=self.save_marks).pack(side="left")
        ttk.Button(actions, text="Generate result", command=self.show_result).pack(side="right")
        return tab

    def build_courses_tab(self, parent):
        tab = ttk.Frame(parent, padding=8)
        self.courses_tree = table(tab, {"Code": 80, "Title": 340, "Credit hours": 100})
        self.courses_tree.pack(fill="both", expand=True)
        add = ttk.LabelFrame(tab, text="Add course", padding=8)
        add.pack(fill="x", pady=(8, 0))
        course_vars = form(add, ["Code", "Title", "Credit hours"])
        ttk.Button(add, text="Add course", command=lambda: self.add_course(*course_vars)).grid(
            row=3, column=1, sticky="e", pady=(4, 0))
        return tab

    # ---------- display ----------

    def refresh(self):
        ranked = sorted(self.school.students.values(), key=lambda s: s.cgpa(), reverse=True)
        fill(self.students_tree, [(s.roll_no, s.name, s.program, f"{s.cgpa():.2f}") for s in ranked])
        fill(self.courses_tree, [(c.code, c.title, c.credit_hours) for c in self.school.courses.values()])
        self.course_box["values"] = list(self.school.courses)
        self.show_student()

    def selected_student(self):
        selected = self.students_tree.selection()
        return self.school.students[selected[0]] if selected else None

    def show_student(self):
        student = self.selected_student()
        if student is None:
            self.detail.config(text="Select a student to see their courses")
            fill(self.enroll_tree, [])
            self.summary.config(text="")
        else:
            self.detail.config(text=f"Courses of {student.name} ({student.roll_no}, {student.program})")
            fill(self.enroll_tree, [(code, e.course.title, e.course.credit_hours, e.semester,
                                     "-" if e.marks is None else e.marks, e.grade or "-")
                                    for code, e in student.enrollments.items()])
            gpas = [f"Semester {sem} GPA: {student.semester_gpa(sem):.2f}" for sem in student.semesters()]
            self.summary.config(text="     ".join(gpas + [f"CGPA: {student.cgpa():.2f}"]))
        self.show_selection()

    def show_selection(self):
        student, codes = self.selected_student(), self.enroll_tree.selection()
        if not student or not codes:
            self.selection_info.config(text="Tip: select one course to enter marks, or several (Ctrl/Shift+click) to calculate their GPA")
            return
        self.selection_info.config(text=f"GPA of selected courses: {student.gpa(codes):.2f}")
        if len(codes) == 1:
            marks = student.enrollments[codes[0]].marks
            self.marks_var.set("" if marks is None else marks)

    def show_result(self):
        student = self.selected_student()
        if student is None:
            messagebox.showinfo("Generate result", "Select a student first", parent=self)
            return
        window = tk.Toplevel(self)
        window.title(f"Result card - {student.name}")
        text = tk.Text(window, font="TkFixedFont", width=95, height=30, padx=12, pady=12)
        text.insert("1.0", result_card(student))
        text.config(state="disabled")
        text.pack(fill="both", expand=True)

    # ---------- actions ----------

    def run(self, action):
        """Apply a change; on error show it, on success save and redraw. Returns True on success."""
        try:
            action()
        except (KeyError, ValueError) as e:
            messagebox.showerror("Error", e.args[0], parent=self)
            return False
        storage.save(self.school, self.data_file)
        self.refresh()
        return True

    def require_student(self):
        student = self.selected_student()
        if student is None:
            raise ValueError("Select a student first")
        return student

    def add_student(self, roll, name, program):
        roll_no = roll.get().strip().upper()
        if self.run(lambda: self.school.add_student(roll_no, name.get().strip(), program.get().strip().upper())):
            for var in (roll, name, program):
                var.set("")
            self.students_tree.selection_set(roll_no)

    def add_course(self, code, title, credits):
        if self.run(lambda: self.school.add_course(code.get().strip().upper(), title.get().strip(),
                                                   number(credits, int, "Credit hours"))):
            for var in (code, title, credits):
                var.set("")

    def enroll(self):
        self.run(lambda: self.school.enroll(self.require_student().roll_no, self.course_var.get(),
                                            number(self.semester_var, int, "Semester")))

    def save_marks(self):
        def action():
            codes = self.enroll_tree.selection()
            if len(codes) != 1:
                raise ValueError("Select exactly one course in the table first")
            self.school.enter_marks(self.require_student().roll_no, codes[0], number(self.marks_var, float, "Marks"))
        self.run(action)


if __name__ == "__main__":
    App().mainloop()
