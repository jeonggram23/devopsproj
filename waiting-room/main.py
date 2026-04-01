from fastapi import FastAPI, Request, HTTPException
import redis
import os

app = FastAPI()

# K8s 내부망을 통해 방금 만든 Redis 마스터 노드(my-redis-master-0)에 연결
# K8s Service 이름인 'my-redis-master'로 찌르면 알아서 0번 파드로 찾아갑니다.
r = redis.Redis(host=os.getenv("REDIS_HOST", "my-redis-master"), port=6379, decode_responses=True)

MAX_USERS = 3  # 실습을 위해 대기열 통과 인원을 딱 3명으로 제한!

@app.get("/auth")
def check_auth(request: Request):
    # 접속할 때마다 Redis의 'active_users' 카운트를 1씩 증가
    current_users = r.incr("active_users")
    
    # 3명 이하라면 통과 (200 OK) -> NGINX가 진짜 웹페이지로 보내줌
    if current_users <= MAX_USERS:
        return {"status": "ok"}
    
    # 3명 초과라면 튕겨냄 (401 Unauthorized) -> 들어가지 못했으니 인원수를 다시 빼줌
    r.decr("active_users")
    raise HTTPException(status_code=401, detail="대기 인원이 꽉 찼습니다!")

# (테스트용) 꽉 찬 인원수를 다시 0으로 초기화하는 API
@app.get("/reset")
def reset_users():
    r.set("active_users", 0)
    return {"message": "초기화 완료"}
