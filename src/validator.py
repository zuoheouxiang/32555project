
import re


class Validator:

    # 验证邮箱格式
    @staticmethod
    def is_valid_email(email):
        if not isinstance(email, str):
            return False

        pattern = r"[a-zA-Z]+(\.[a-zA-Z]+)*@university\.com"
        return re.fullmatch(pattern, email) is not None

    # 验证密码安全性
    @staticmethod
    def is_valid_password(password):
        if not isinstance(password, str):
            return False

        # 至少12个字符，不允许空格
        if len(password) < 12 or any(c.isspace() for c in password):
            return False

        # 至少包含一个大写字母
        if not re.search(r"[A-Z]", password):
            return False

        # 至少包含一个小写字母
        if not re.search(r"[a-z]", password):
            return False

        # 至少包含6个数字
        if len(re.findall(r"[0-9]", password)) < 6:
            return False

        # 至少包含一个特殊字符
        if not re.search(r"[^a-zA-Z0-9\s]", password):
            return False

        return True

    # 检查新密码是否与旧密码相同
    @staticmethod
    def is_new_password(old_password, new_password):
        return old_password != new_password
