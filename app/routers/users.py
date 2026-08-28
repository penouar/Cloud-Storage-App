from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.database import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.security import create_access_token, get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

password_hasher = PasswordHasher()

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user=db.query(User).filter(
        (User.username == user_data.username) |
        (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists"
        )
    
   
    hashed_password = password_hasher.hash(user_data.password)

    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )

    # Add, commit, refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    
    return new_user

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    user_login= db.query(User).filter(
        (User.username==user_data.username) |
        (User.email==user_data.email)
    ).first()

    if user_login is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    try:
        password_hasher.verify(user_login.password_hash, user_data.password)
    except VerifyMismatchError:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(user_login.user_id)})


    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

    

