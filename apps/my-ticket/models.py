from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# users 테이블 구조
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String) # 실제로는 해싱(암호화)해서 넣어야 합니다
    is_admin = Column(Boolean, default=False) # 어드민 권한 여부