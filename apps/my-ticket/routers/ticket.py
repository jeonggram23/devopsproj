from fastapi import APIRouter, HTTPException
from database import redis_client

router = APIRouter(prefix="/ticket", tags=["티켓 구매 및 대기열"])

# 총 티켓 수 설정
TOTAL_TICKETS = 100

@router.post("/init")
def init_tickets():
    """테스트를 위해 티켓 수를 100장으로 초기화합니다."""
    redis_client.set("available_tickets", TOTAL_TICKETS)
    return {"message": f"티켓이 {TOTAL_TICKETS}장으로 세팅되었습니다. 티켓팅 시작!"}

@router.post("/buy")
def buy_ticket(session_token: str):
    """Redis 세션을 확인하고 선착순으로 티켓을 발급합니다."""
    # 1. 로그인한 유저인지 출입증(토큰) 확인
    username = redis_client.get(session_token)
    if not username:
        raise HTTPException(status_code=401, detail="로그인이 풀렸거나 유효하지 않은 출입증입니다.")

    # 2. [핵심] Redis의 DECR(1씩 감소) 명령어로 티켓 차감
    # 이 명령어는 1만 명이 동시에 요청해도 절대 꼬이지 않고 1명씩 순차적으로 처리됩니다.
    tickets_left = redis_client.decr("available_tickets")

    # 3. 남은 티켓이 0 미만이면 매진 처리
    if tickets_left < 0:
        # 0 미만으로 내려간 값을 다시 0으로 복구
        redis_client.incr("available_tickets")
        raise HTTPException(status_code=400, detail="🎫 앗! 티켓이 모두 매진되었습니다.")

    return {
        "message": "🎉 티켓 구매 성공!",
        "buyer": username,
        "tickets_remaining": tickets_left
    }