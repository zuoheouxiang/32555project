
import sys
sys.dont_write_bytecode = True

from getpass import getpass
from enrolment_system import EnrolmentSystem
from student import Student
from subject import Subject
from validator import Validator


# 开发阶段允许使用CLI测试学生功能
# GUI完成后修改为False
ENABLE_STUDENT_CLI = True


# 学生账号控制
class StudentAccountControl:
    def __init__(self, db):
        self.db = db

    # 注册账号
    def register(self, name, email, password):
        if not name.strip():
            return None, "Name cannot be empty."

        if not Validator.is_valid_email(email):
            return None, "Invalid email format."

        if not Validator.is_valid_password(password):
            return None, "Invalid password format."

        if self.db.find_student_by_email(email):
            return None, "Email already registered."

        student_id = self.db.generate_student_id()
        student = Student(student_id, name, email, password)
        self.db.add_student(student)

        return student, f"Registration successful! ID: {student_id}"

    # 登录账号
    def login(self, email, password):
        student = self.db.find_student_by_email(email)

        if student is None or student.password != password:
            return None, "Incorrect email or password."

        return student, "Login successful!"

    # 修改密码
    def change_password(self, student, new_password):
        if not Validator.is_valid_password(new_password):
            return False, "Invalid password format."

        if not Validator.is_new_password(student.password, new_password):
            return False, "New password cannot be the same as the old password."

        student.password = new_password
        self.db.save_data()
        return True, "Password changed successfully!"


# 学生选课控制
class StudentEnrolmentControl:
    def __init__(self, db):
        self.db = db

    # 选课
    def enrol_subject(self, student):
        if not student.can_enrol():
            return False, "Maximum 4 subjects allowed."

        subject_id = self.db.generate_subject_id()
        subject = Subject(subject_id)
        student.enrol(subject)
        self.db.save_data()

        return True, f"Subject {subject_id} enrolled successfully."

    # 退课
    def remove_subject(self, student, subject_id):
        if not student.remove_subject(subject_id):
            return False, "Subject not found."

        self.db.save_data()
        return True, "Subject removed successfully."

    # 获取课程列表
    def view_enrolment(self, student):
        return student.subjects


# 管理员控制
class AdminControl:
    def __init__(self, db):
        self.db = db

    # 查看所有学生
    def view_students(self):
        return self.db.get_students()

    # 按成绩等级分组
    def group_by_grade(self):
        groups = {"HD": [], "D": [], "C": [], "P": [], "Z": []}

        for student in self.db.get_students():
            if student.subjects:
                groups[student.overall_grade()].append(student)

        return groups

    # 按PASS和FAIL分类
    def categorize_pass_fail(self):
        groups = {"PASS": [], "FAIL": []}

        for student in self.db.get_students():
            if student.subjects:
                status = "PASS" if student.is_pass() else "FAIL"
                groups[status].append(student)

        return groups

    # 删除指定学生
    def remove_student(self, student_id):
        return self.db.remove_student(student_id)

    # 清空所有学生
    def clear_students(self):
        self.db.clear_students()


# 主程序
class App:
    def __init__(self):
        # 所有控制器共用一个数据库
        self.db = EnrolmentSystem()
        self.account = StudentAccountControl(self.db)
        self.enrolment = StudentEnrolmentControl(self.db)
        self.admin = AdminControl(self.db)

    # 学生注册和登录菜单
    def student_menu(self):
        while True:
            print("\n--- Student System ---")
            print("(L) Login")
            print("(R) Register")
            print("(X) Exit")

            choice = input("Choice: ").lower()

            if choice == "r":
                name = input("Name: ")
                email = input("Email: ")
                password = getpass("Password: ")

                student, message = self.account.register(
                    name, email, password
                )
                print(message)

            elif choice == "l":
                email = input("Email: ")
                password = getpass("Password: ")

                student, message = self.account.login(
                    email, password
                )
                print(message)

                if student:
                    self.enrolment_menu(student)

            elif choice == "x":
                break
            else:
                print("Invalid option.")

    # 学生选课菜单
    def enrolment_menu(self, student):
        while True:
            print(f"\n--- Welcome, {student.name} ---")
            print("(C) Change Password")
            print("(E) Enrol Subject")
            print("(R) Remove Subject")
            print("(S) Show Enrolment")
            print("(X) Logout")

            choice = input("Choice: ").lower()

            if choice == "c":
                new_pw = getpass("New password: ")
                _, message = self.account.change_password(
                    student, new_pw
                )
                print(message)

            elif choice == "e":
                _, message = self.enrolment.enrol_subject(student)
                print(message)

            elif choice == "r":
                subject_id = input("Subject ID: ")
                _, message = self.enrolment.remove_subject(
                    student, subject_id
                )
                print(message)

            elif choice == "s":
                subjects = self.enrolment.view_enrolment(student)

                if not subjects:
                    print("No subjects enrolled.")
                else:
                    print("\nID      MARK    GRADE")
                    for subject in subjects:
                        print(
                            f"{subject.subject_id:<8}"
                            f"{subject.mark:<8}"
                            f"{subject.grade}"
                        )

                    print(f"Average: {student.average_mark():.2f}")
                    print(f"Overall grade: {student.overall_grade()}")

            elif choice == "x":
                break
            else:
                print("Invalid option.")

    # 管理员菜单
    def admin_menu(self):
        while True:
            print("\n--- Admin System ---")
            print("(C) Clear All Students")
            print("(G) Group by Grade")
            print("(P) PASS/FAIL Classification")
            print("(R) Remove Student")
            print("(S) Show All Students")
            print("(X) Exit")

            choice = input("Choice: ").lower()

            if choice == "s":
                students = self.admin.view_students()

                if not students:
                    print("No students found.")

                for student in students:
                    print(student)

            elif choice == "g":
                groups = self.admin.group_by_grade()

                for grade, students in groups.items():
                    print(f"\n{grade}:")
                    for student in students:
                        print(student)

            elif choice == "p":
                groups = self.admin.categorize_pass_fail()

                for status, students in groups.items():
                    print(f"\n{status}:")
                    for student in students:
                        print(student)

            elif choice == "r":
                student_id = input("Student ID: ")

                if self.admin.remove_student(student_id):
                    print("Student removed successfully.")
                else:
                    print("Student not found.")

            elif choice == "c":
                confirm = input("Clear ALL students? (yes/no): ")

                if confirm.lower() == "yes":
                    self.admin.clear_students()
                    print("All students cleared.")
                else:
                    print("Operation cancelled.")

            elif choice == "x":
                break
            else:
                print("Invalid option.")

    # 大学系统主菜单
    def run(self):
        while True:
            print("\n=== University Enrolment System ===")
            print("(A) Admin System")

            if ENABLE_STUDENT_CLI:
                print("(S) Student System")

            print("(X) Exit")

            choice = input("Choice: ").lower()

            if choice == "a":
                self.admin_menu()

            elif choice == "s" and ENABLE_STUDENT_CLI:
                self.student_menu()

            elif choice == "x":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")


# 程序入口
if __name__ == "__main__":
    App().run()


