"""LangGraph 에이전트를 FastAPI 로 서빙하기.

웹페이지를 스크래핑해 답하는 LangGraph 에이전트를 두 가지 방식의 API 로 노출한다:
- POST /ai-assist/invoke : 요청 한 번에 최종 답변을 JSON 으로 반환 (동기 단발)
- GET  /ai-assist/stream : 단계별 진행을 SSE(Server-Sent Events)로 실시간 스트리밍

실행: uv run uvicorn main:app --reload
문서: http://127.0.0.1:8000/docs
필요 키: OPENAI_API_KEY (.env)
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Annotated, List
from typing_extensions import TypedDict

from dotenv import load_dotenv
import os
import json

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition, ToolNode

load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 가 .env 에 없습니다"
os.environ.setdefault("USER_AGENT", "ai-agent-study")

# ----------------------------
# 1. FastAPI 앱
# ----------------------------
app = FastAPI()


@app.get("/")
async def root():
    return "Hello World"


# ----------------------------
# 2. LangGraph 에이전트 정의
#    [basics] State(add_messages) + chatbot ⇄ web_scraper 루프
# ----------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model="gpt-4o")


@tool
def scrape_webpages(urls: List[str]) -> str:
    """Scrape the provided web pages for detailed information."""
    docs = WebBaseLoader(urls).load()
    return "\n\n".join(
        f'<Document name="{d.metadata.get("title", "")}">\n{d.page_content}\n</Document>'
        for d in docs
    )


# 비동기 노드 — FastAPI 의 async 엔드포인트와 궁합이 좋다
async def chatbot(state: State):
    llm_with_tools = llm.bind_tools([scrape_webpages])
    response = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("web_scraper", ToolNode([scrape_webpages], name="web_scraper"))
graph_builder.set_entry_point("chatbot")
graph_builder.add_conditional_edges(
    "chatbot", tools_condition, {"tools": "web_scraper", END: END}
)
graph_builder.add_edge("web_scraper", "chatbot")
graph = graph_builder.compile()


# ----------------------------
# 3. API 엔드포인트
# ----------------------------
class UserInput(BaseModel):
    message: str


@app.post("/ai-assist/invoke")
async def invoke(user_input: UserInput):
    """동기 단발: 최종 답변만 JSON 으로 반환."""
    try:
        response = await graph.ainvoke(
            {"messages": [HumanMessage(content=user_input.message)]}
        )
        return JSONResponse(
            content={"content": response["messages"][-1].content},
            media_type="application/json; charset=utf-8",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai-assist/stream")
async def stream(message: str = ""):
    """스트리밍: 각 노드 업데이트를 SSE 로 실시간 전송."""
    async def event_generator():
        async for chunk in graph.astream({"messages": [HumanMessage(content=message)]}):
            try:
                serializable = {
                    node: value["messages"][0].content for node, value in chunk.items()
                }
                yield f"[Node update] {json.dumps(serializable, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"Error processing chunk: {str(e)}\n\n"

    return StreamingResponse(
        event_generator(), media_type="text/event-stream; charset=utf-8"
    )
