"""学生管理系统基本功能测试。运行：python -B test_app.py"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from enrolment_system import EnrolmentSystem
from student import Student
from subject import Subject
from validator import Validator
from App import StudentAccountControl, StudentEnrolmentControl, AdminControl


class TestUniSystem(unittest.TestCase):
    def setUp(self):
        # 创建临时数据库，避免污染真实 students.data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "students.data"
        # 原版 EnrolmentSystem 没有路径参数，临时替换实例的数据路径
        with patch.object(EnrolmentSystem, "load_data", lambda db: None):
            self.db = EnrolmentSystem()
        self.db.file_name = self.data_file
        self.db.save_data()
        self.account = StudentAccountControl(self.db)
        self.enrolment = StudentEnrolmentControl(self.db)
        self.admin = AdminControl(self.db)

    def register(self, email="john.smith@university.com", password="Abc@12345678"):
        student, message = self.account.register("John Smith", email, password)
        self.assertIsNotNone(student, message)
        return student

    def test_email_validation(self):
        for value in ("john.smith@university.com", "john@university.com"):
            with self.subTest(email=value):
                self.assertTrue(Validator.is_valid_email(value))
        for value in ("john@gmail.com", "john@university", "john123@university.com", "", None):
            with self.subTest(email=value):
                self.assertFalse(Validator.is_valid_email(value))

    def test_password_validation(self):
        for value in ("Abc@12345678", "Hello#123456"):
            with self.subTest(password=value):
                self.assertTrue(Validator.is_valid_password(value))
        for value in ("abc@12345678", "ABC@12345678", "Abc@12345", "Abc12345678", "Abc@1234 5678", None):
            with self.subTest(password=value):
                self.assertFalse(Validator.is_valid_password(value))
        self.assertFalse(Validator.is_new_password("Abc@12345678", "Abc@12345678"))

    def test_registration_and_login(self):
        student = self.register()
        self.assertEqual(len(student.student_id), 6)
        self.assertTrue(student.student_id.isdigit())
        self.assertIs(self.db.find_student_by_email(student.email), student)
        duplicate, _ = self.account.register("Other", student.email, "Abc@12345678")
        self.assertIsNone(duplicate)
        wrong, _ = self.account.login(student.email, "incorrect")
        self.assertIsNone(wrong)
        logged_in, _ = self.account.login(student.email, "Abc@12345678")
        self.assertEqual(logged_in.student_id, student.student_id)

    def test_registration_invalid_inputs(self):
        for name, email, password in (
            (" ", "john.smith@university.com", "Abc@12345678"),
            ("John", "john@gmail.com", "Abc@12345678"),
            ("John", "john.smith@university.com", "abc123"),
        ):
            with self.subTest(name=name, email=email, password=password):
                student, _ = self.account.register(name, email, password)
                self.assertIsNone(student)
        self.assertEqual(len(self.db.get_students()), 0)

    def test_password_change(self):
        student = self.register()
        success, _ = self.account.change_password(student, "Abc@12345678")
        self.assertFalse(success)
        success, _ = self.account.change_password(student, "abc123")
        self.assertFalse(success)
        success, _ = self.account.change_password(student, "New@87654321")
        self.assertTrue(success)
        self.assertIsNone(self.account.login(student.email, "Abc@12345678")[0])
        self.assertIsNotNone(self.account.login(student.email, "New@87654321")[0])

    def test_enrolment_limit_and_removal(self):
        student = self.register()
        for _ in range(4):
            success, message = self.enrolment.enrol_subject(student)
            self.assertTrue(success, message)
        self.assertEqual(len(student.subjects), 4)
        ids = [subject.subject_id for subject in student.subjects]
        self.assertEqual(len(set(ids)), 4)
        for subject in student.subjects:
            self.assertEqual(len(subject.subject_id), 3)
            self.assertTrue(25 <= subject.mark <= 100)
            self.assertIn(subject.grade, ("Z", "P", "C", "D", "HD"))
        self.assertFalse(self.enrolment.enrol_subject(student)[0])
        self.assertFalse(self.enrolment.remove_subject(student, "000")[0])
        self.assertTrue(self.enrolment.remove_subject(student, ids[0])[0])
        self.assertEqual(len(student.subjects), 3)
        self.assertTrue(self.enrolment.enrol_subject(student)[0])

    def test_grade_boundaries(self):
        expected = {25: "Z", 49: "Z", 50: "P", 64: "P", 65: "C", 74: "C", 75: "D", 84: "D", 85: "HD", 100: "HD"}
        for mark, grade in expected.items():
            with self.subTest(mark=mark):
                subject = Subject("123")
                subject.mark = mark
                self.assertEqual(subject.calculate_grade(), grade)

    def test_admin_and_persistence(self):
        student = self.register()
        # 手动设置成绩，使分组结果可预测
        subject = Subject("123")
        subject.mark = 85
        subject.grade = subject.calculate_grade()
        student.enrol(subject)
        self.db.save_data()
        self.assertEqual(len(self.admin.view_students()), 1)
        self.assertIn(student, self.admin.group_by_grade()["HD"])
        self.assertIn(student, self.admin.categorize_pass_fail()["PASS"])
        # 用独立读取对象验证 JSON 持久化
        with patch.object(EnrolmentSystem, "load_data", lambda db: None):
            reloaded = EnrolmentSystem()
        reloaded.file_name = self.data_file
        reloaded.load_data()
        loaded = reloaded.find_student(student.student_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.subjects[0].mark, 85)
        self.assertFalse(self.admin.remove_student("000000"))
        self.assertTrue(self.admin.remove_student(student.student_id))
        self.assertEqual(self.admin.view_students(), [])
        self.register("jane.smith@university.com")
        self.admin.clear_students()
        self.assertEqual(self.admin.view_students(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
