"""멀티 MCP 서버 + Supervisor 클라이언트.

두 MCP 서버(file:8000, web:8001)를 MultiServerMCPClient 로 동시에 연결하고,
각 서버의 도구를 가진 전문 에이전트(file_searcher / web_searcher)를
supervisor 가 지휘하는 멀티에이전트 그래프를 구성한다.

실행 순서:
  1) 터미널 A:  uv run python file_search_server.py
  2) 터미널 B:  uv run python web_search_server.py
  3) 터미널 C:  uv run python multi_client.py
필요 키: OPENAI_API_KEY, TAVILY_API_KEY (+ 날씨는 OPENWEATHERMAP_API_KEY)
"""
from dotenv import load_dotenv
import os
import asyncio
import sys

from typing import Literal
from typing_extensions import TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 윈도우에서 asyncio + subprocess 호환
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 가 .env 에 없습니다"

model = ChatOpenAI(model="gpt-4o")

# [basics 복습] supervisor 가 고를 작업자 목록
members = ["file_searcher", "web_searcher"]
options = members + ["FINISH"]


class Router(TypedDict):
    """다음 작업자. 필요 없으면 FINISH."""
    next: Literal[*options]


class State(MessagesState):
    next: str


async def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 두 MCP 서버를 SSE 로 동시 연결 (langchain-mcp-adapters 신버전 API)
    client = MultiServerMCPClient(
        {
            "file": {"url": "http://localhost:8000/sse", "transport": "sse"},
            "web": {"url": "http://localhost:8001/sse", "transport": "sse"},
        }
    )

    # 서버별 도구 로드 (get_tools(server_name=...))
    file_tools = await client.get_tools(server_name="file")
    web_tools = await client.get_tools(server_name="web")

    system_prompt = (
        "You are a supervisor managing a conversation between these workers: "
        f"{members}. Given the user request, respond with the worker to act next. "
        "Each worker performs a task and reports results. When finished, respond with FINISH."
    )

    # [basics 복습] supervisor: 구조화 출력으로 다음 작업자/FINISH 결정
    async def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = await model.with_structured_output(Router).ainvoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END
        return Command(goto=goto, update={"next": goto})

    # 파일 검색 에이전트 (file 서버 도구)
    file_searcher = create_react_agent(model, file_tools)

    async def file_search_node(state: State) -> Command[Literal["supervisor"]]:
        result = await file_searcher.ainvoke(state)
        return Command(
            update={"messages": [HumanMessage(content=result["messages"][-1].content, name="file_searcher")]},
            goto="supervisor",
        )

    # 웹 검색 에이전트 (web 서버 도구)
    web_searcher = create_react_agent(model, web_tools)

    async def web_search_node(state: State) -> Command[Literal["supervisor"]]:
        result = await web_searcher.ainvoke(state)
        return Command(
            update={"messages": [HumanMessage(content=result["messages"][-1].content, name="web_searcher")]},
            goto="supervisor",
        )

    # [basics 복습] Supervisor 그래프 조립
    graph_builder = StateGraph(State)
    graph_builder.add_edge(START, "supervisor")
    graph_builder.add_node("supervisor", supervisor_node)
    graph_builder.add_node("file_searcher", file_search_node)
    graph_builder.add_node("web_searcher", web_search_node)
    graph = graph_builder.compile(checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "1"}}
    while True:
        try:
            user_input = input("질문을 입력하세요: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("안녕히 가세요!")
                break

            print("=====RESPONSE=====")
            async for namespace, chunk in graph.astream(
                {"messages": user_input},
                stream_mode="updates",
                subgraphs=True,
                config=config,
            ):
                for node_name, node_chunk in chunk.items():
                    if isinstance(node_chunk, dict) and "messages" in node_chunk:
                        node_chunk["messages"][-1].pretty_print()
                    else:
                        print(node_chunk)
        except Exception as e:
            print(f"종료합니다. {e}")
            break


if __name__ == "__main__":
    asyncio.run(run())
