import jwt
import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib

SECRET_KEY = "shine-brighter-than-the-heavens!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()


def create_access_token(id: int, role: str, tz: str = "", salon_id: int = 0):
    try:
        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
        "id": id,
        "role": role,
        "tz": tz,
        "salon_id": salon_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + access_token_expires
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception:
        raise

class TokenData(BaseModel):
    id: int
    role: str
    tz: str
    salon_id: int

def decode_jwt(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")
        role: str = payload.get("role")
        tz: str = payload.get("tz")
        salon_id: int = payload.get("salon_id")
        if id is None or role is None:
            return None
        return TokenData(id=id, role=role, tz=tz, salon_id=salon_id)
    except jwt.PyJWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    token = credentials.credentials
    token_data = decode_jwt(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return token_data

def require_client_role(
        user: TokenData = Depends(get_current_user)
) -> TokenData:
    if user.role != "client":
        raise HTTPException(
            status_code=403,
            detail="Access denied: client role required"
        )
    return user

def require_admin(
        user: TokenData = Depends(get_current_user)
) -> TokenData:
    if user.role == "staff" and 1000 >= user.id > 400:
        return user
    raise HTTPException(status_code=403,
                        detail="Access denied: admin role required")

def require_cosmetologist(
        user: TokenData = Depends(get_current_user)
) -> TokenData:
    if user.role == "staff" and user.id > 1000:
        return user
    raise HTTPException(status_code=403,
                        detail="Access denied: cosmetologist role required")

def require_head(
        user: TokenData = Depends(get_current_user)
) -> TokenData:
    if user.role == "staff" and 100 < user.id <= 400:
        return user
    raise HTTPException(status_code=403,
                        detail="Access denied: head role required")
def require_acc(
        user: TokenData = Depends(get_current_user)
) -> TokenData:
    if user.role == "staff" and user.id <= 100:
        return user
    raise HTTPException(status_code=403,
                        detail="Access denied: accountant role required")

class PaginatedResponse(BaseModel):
    items: List[Any]
    last: int

def password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()