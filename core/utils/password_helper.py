import bcrypt

class PasswordHelper:
  @staticmethod
  def get_hash(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

  @staticmethod
  def check_hash(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))