import random
import string
import re


class StringHelper:
    @staticmethod
    def random_string(length):
        return "".join(
            random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits,
                k=length,
            )
        )

    @staticmethod
    def random_string_number(length):
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def validate_email(email):
        return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

    @staticmethod
    def validate_password(password):
        return re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,15}$", password
        )
