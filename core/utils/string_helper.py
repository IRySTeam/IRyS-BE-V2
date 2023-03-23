import random
import string

class StringHelper:
  @staticmethod
  def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
