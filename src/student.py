
from subject import Subject


class Student:
    # 初始化学生信息
    def __init__(self, student_id, name, email, password, subjects=None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password = password
        self.subjects = subjects if subjects is not None else []

    # 检查是否还能选课（最多4门）
    def can_enrol(self):
        return len(self.subjects) < 4

    # 添加一门课程
    def enrol(self, subject):
        if not self.can_enrol():
            return False

        self.subjects.append(subject)
        return True

    # 根据课程ID删除课程
    def remove_subject(self, subject_id):
        for subject in self.subjects:
            if subject.subject_id == subject_id:
                self.subjects.remove(subject)
                return True

        return False

    # 计算所有课程的平均分
    def average_mark(self):
        if not self.subjects:
            return 0

        total = sum(subject.mark for subject in self.subjects)
        return total / len(self.subjects)

    # 根据平均分计算总体等级
    def overall_grade(self):
        mark = self.average_mark()

        if mark >= 85:
            return "HD"
        elif mark >= 75:
            return "D"
        elif mark >= 65:
            return "C"
        elif mark >= 50:
            return "P"
        else:
            return "Z"

    # 判断学生是否通过（平均分至少50）
    def is_pass(self):
        return self.average_mark() >= 50

    # 转换成字典，用于JSON保存
    def to_dict(self):
        return {
            "id": self.student_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "subjects": [s.to_dict() for s in self.subjects]
        }

    # 从JSON数据恢复学生对象
    @classmethod
    def from_dict(cls, data):
        subjects = [
            Subject.from_dict(s)
            for s in data.get("subjects", [])
        ]

        return cls(
            data["id"],
            data["name"],
            data["email"],
            data["password"],
            subjects
        )

    # 打印学生基本信息
    def __str__(self):
        return (
            f"{self.name} :: {self.student_id} --> "
            f"GRADE: {self.overall_grade()} - "
            f"MARK: {self.average_mark():.2f}"
        )
