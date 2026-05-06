from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake user store
fake_user = {
    "username": "demo",
    "full_name": "Demo User",
    "hashed_password": pwd_context.hash("password123"),
     "role": "admin" 
}

fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    },
    "creator1": {
        "id": 2,
        "username": "creator1",
        "full_name": "Creator One",
        "hashed_password": pwd_context.hash("creator123"),
        "role": "creator"
    },
    "creator2": {
        "id": 3,
        "username": "creator2",
        "full_name": "Creator Two",
        "hashed_password": pwd_context.hash("creator123"),
        "role": "creator"
    }
}



def require_admin(user: dict):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# def authenticate_user(username: str, password: str):
#     if username != fake_user["username"]:
#         return None
#     if not verify_password(password, fake_user["hashed_password"]):
#         return None
#     return fake_user

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    # Look up the user in the fake DB
    user = fake_users_db.get(username)
    if user is None:
        raise cred_exc

    return user
