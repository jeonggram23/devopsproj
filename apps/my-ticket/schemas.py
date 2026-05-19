from pydantic import BaseModel

# 클라이언트가 회원가입할 때 보내는 데이터 형태
class UserCreate(BaseModel):
    username: str
    password: str

# 서버가 클라이언트에게 응답해줄 데이터 형태 (비밀번호 제외)
class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True # ORM 객체를 JSON으로 자동 변환해주는 마법