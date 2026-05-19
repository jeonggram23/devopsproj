from fastapi import FastAPI
from database import engine, Base
from routers import auth, board, ticket

# 앱이 켜질 때 models.py를 읽고 DB에 테이블을 자동으로 생성! (ORM의 위력)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Ticket API", description="FastAPI + ORM 아키텍처")

# 쪼개놓은 라우터들(기능들)을 메인 앱에 등록
app.include_router(auth.router)
# app.include_router(board.router)  # 아직 파일 안이 비어있으니 일단 주석 처리
app.include_router(ticket.router) # 아직 파일 안이 비어있으니 일단 주석 처리

@app.get("/")
def read_root():
    return {"message": "실무형 ORM 백엔드 서버가 완벽하게 준비되었습니다!"}