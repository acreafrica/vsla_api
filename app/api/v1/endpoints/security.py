# security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import requests
import random
import uuid
# JWT settings
SECRET_KEY = "your-secret-key"  # Replace with a secure value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_blacklist = set()
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def decode_access_token(token: str):
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         return None
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token with a unique jti (for logout tracking)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    jti = str(uuid.uuid4())  # unique token ID
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """Decode JWT and check if it's blacklisted."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti in token_blacklist:
            return None  # token revoked
        return payload
    except JWTError:
        return None

def revoke_token(token: str):
    """Invalidate a JWT by adding its jti to blacklist."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            token_blacklist.add(jti)
            return True
    except JWTError:
        pass
    return False
def generate_otp_code(length: int = 6) -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def create_reset_token(user_id: str, expires_minutes: int = 15):
    return create_access_token(
        data={"sub": user_id, "reset": True},
        expires_delta=timedelta(minutes=expires_minutes)
    )
async def send_sms_via_gateway(phone: str, message: str):
    try:
        reqUrl = f"http://20.164.220.70:85/digibimaprod/initiatesms?phoneno={phone}&message={message}"
        headersList = {
            "Accept": "*/*",
            "User-Agent": "FastAPI Service"
        }
        response = requests.request("POST", reqUrl, headers=headersList)
        return response.json()
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return None