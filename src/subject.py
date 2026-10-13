
import random


class Subject:
    # 初始化课程，自动生成随机成绩
    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.mark = random.randint(25, 100)
        self.grade = self.calculate_grade()

    # 根据成绩计算等级
    def calculate_grade(self):
        if self.mark >= 85:
            return "HD"
        elif self.mark >= 75:
            return "D"
        elif self.mark >= 65:
            return "C"
        elif self.mark >= 50:
            return "P"
        else:
            return "Z"

    # 转换为字典，方便保存到JSON
    def to_dict(self):
        return {
            "id": self.subject_id,
            "mark": self.mark,
            "grade": self.grade
        }

    # 从JSON数据恢复课程对象
    @classmethod
    def from_dict(cls, data):
        subject = cls(data["id"])
        subject.mark = data["mark"]
        subject.grade = subject.calculate_grade()
        return subject
