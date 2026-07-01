"""FastAPI 기초 — HTTP 메서드와 라우팅.

LangGraph 없이 FastAPI 자체를 익히는 최소 예제.
실행: uv run uvicorn basics:app --reload
문서: http://127.0.0.1:8000/docs  (Swagger UI 자동 생성)
"""
from fastapi import FastAPI, HTTPException

app = FastAPI()


# GET: 서버에 저장된 데이터를 요청할 때
@app.get("/")
async def root():
    return "Hello, World!"


@app.get("/test")
async def test():
    return {"message": "Hello, FastAPI!"}


# 간단한 인메모리 저장소 (학습용)
messages: dict[int, str] = {}


# POST: 새 데이터를 서버에 보낼 때(생성)
@app.post("/message")
async def post_message(message: str):
    new_id = (max(messages) + 1) if messages else 1
    messages[new_id] = message
    return {"id": new_id, "message": message}


# PUT: 기존 데이터를 수정(덮어쓰기)할 때
@app.put("/message/{message_id}")
async def put_message(message_id: int, new_message: str):
    messages[message_id] = new_message
    return {"message": f"Message {message_id} updated to '{new_message}'"}


# DELETE: 특정 데이터를 삭제할 때
@app.delete("/message/{message_id}")
async def delete_message(message_id: int):
    if message_id not in messages:
        raise HTTPException(status_code=404, detail="Message not found")
    del messages[message_id]
    return {"message": f"Message {message_id} deleted"}
