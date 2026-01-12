import os

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')    # should be kept secret

if not JWT_SECRET_KEY or not JWT_REFRESH_SECRET_KEY:
    raise RuntimeError("JWT secrets not set in environment variables")
