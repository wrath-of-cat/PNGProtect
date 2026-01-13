import hashlib
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def sha256_bytes(data: bytes) -> str:
  """
  Return hex-encoded SHA256 hash of arbitrary bytes.
  """
  return hashlib.sha256(data).hexdigest()


def hash_password(password: str) -> str:
  """
  Hash a password using bcrypt
  """
  return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """
  Verify a password against its hash
  """
  return pwd_context.verify(plain_password, hashed_password)
