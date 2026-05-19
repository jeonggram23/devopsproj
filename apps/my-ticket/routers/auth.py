from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid
import models, schemas
from database import get_db, redis_client

router = APIRouter(prefix="/auth", tags=["인증/회원가입"])

# 실무 표준인 bcrypt 알고리즘으로 비밀번호를 암호화하는 도구
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. 중복 체크
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    # 2. 비밀번호 단방향 암호화 (DB가 털려도 원래 비밀번호를 알 수 없음)
    hashed_password = pwd_context.hash(user.password)
    
    # 3. 암호화된 비밀번호로 DB에 저장
    new_user = models.User(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. DB에서 아이디 검색
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    # 2. 아이디가 없거나, 비밀번호 해시값이 일치하지 않으면 튕겨냄
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호가 틀렸습니다.")
    
    # 3. 로그인 성공! 고유한 출입증(토큰) 난수 생성
    session_token = str(uuid.uuid4())
    
    # 4. Redis에 세션 저장 (키: 토큰, 값: 유저명, 3600초 동안만 유지)
    # RDBMS(PostgreSQL)를 괴롭히지 않고, 초고속 메모리(Redis)에서 출입증을 관리합니다.
    redis_client.setex(session_token, 3600, db_user.username)
    
    return {
        "message": "로그인 성공!", 
        "username": db_user.username,
        "session_token": session_token
    }