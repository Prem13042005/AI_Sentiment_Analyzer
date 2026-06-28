from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas import UserCreate, UserResponse, Token, GoogleLoginRequest
from backend.app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_operator(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new system operator.
    Verifies that the username and email are unique before creating the DB record.
    """
    # Check username uniqueness
    existing_username = db.query(User).filter(User.username == user_in.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Check email uniqueness
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates operator credentials and issues a JWT access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )

    # Issue JWT token
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        user_id=user.id
    )

@router.post("/google", response_model=Token)
def login_with_google(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Registers or logs in a user using Google Sign-In details.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Generate unique alphanumeric username based on email prefix
        import re
        import secrets
        username_base = request.email.split("@")[0]
        username_base = re.sub(r"[^a-zA-Z0-9_]", "", username_base)
        username = username_base
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{username_base}_{counter}"
            counter += 1
            
        random_password = secrets.token_urlsafe(16)
        hashed_pw = get_password_hash(random_password)
        
        user = User(
            username=username,
            email=request.email,
            hashed_password=hashed_pw,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Issue JWT token
    access_token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        user_id=user.id
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the user profile of the currently logged in operator.
    """
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Operator logout request. Client discards the token.
    """
    return {"message": "Logged out successfully"}
