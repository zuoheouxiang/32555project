
import json
import random
from pathlib import Path
from student import Student


class EnrolmentSystem:
    # 初始化数据库，自动读取学生数据
    def __init__(self):
        # 数据文件保存在项目根目录
        self.file_name = Path(__file__).resolve().parent.parent / "students.data"
        self.students = []
        self.load_data()

    # 从JSON文件读取学生数据
    def load_data(self):
        if not self.file_name.exists():
            self.save_data()
            return

        with open(self.file_name, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 将字典转换成Student对象
        self.students = [Student.from_dict(s) for s in data]

    # 将学生数据保存到JSON文件
    def save_data(self):
        data = [s.to_dict() for s in self.students]

        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # 获取所有学生
    def get_students(self):
        return self.students.copy()

    # 根据学生ID查找学生
    def find_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    # 根据邮箱查找学生（忽略大小写）
    def find_student_by_email(self, email):
        for student in self.students:
            if student.email.lower() == email.lower():
                return student
        return None

    # 添加新学生并保存
    def add_student(self, student):
        # 防止重复注册
        if self.find_student_by_email(student.email):
            return False

        self.students.append(student)
        self.save_data()
        return True

    # 删除指定学生
    def remove_student(self, student_id):
        student = self.find_student(student_id)

        if student is None:
            return False

        self.students.remove(student)
        self.save_data()
        return True

    # 清空所有学生数据
    def clear_students(self):
        self.students.clear()
        self.save_data()

    # 生成唯一的6位学生ID
    def generate_student_id(self):
        used_ids = {s.student_id for s in self.students}

        if len(used_ids) >= 999999:
            raise RuntimeError("No available student IDs.")

        while True:
            student_id = str(random.randint(1, 999999)).zfill(6)

            if student_id not in used_ids:
                return student_id

    # 生成唯一的3位课程ID
    def generate_subject_id(self):
        used_ids = {
            sub.subject_id
            for student in self.students
            for sub in student.subjects
        }

        if len(used_ids) >= 999:
            raise RuntimeError("No available subject IDs.")

        while True:
            subject_id = str(random.randint(1, 999)).zfill(3)

            if subject_id not in used_ids:
                return subject_id
