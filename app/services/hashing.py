import hashlib


def sha256_bytes(data: bytes) -> str:
  """
  Return hex-encoded SHA256 hash of arbitrary bytes.
  """
  return hashlib.sha256(data).hexdigest()
