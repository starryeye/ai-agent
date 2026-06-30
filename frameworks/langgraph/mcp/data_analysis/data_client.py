"""데이터 분석 MCP 클라이언트.

data_server.py 를 stdio 로 띄워 그 MCP 도구들을 LangGraph ReAct 에이전트에 연결한다.
langchain-mcp-adapters 가 MCP 도구를 LangChain 도구로 변환해준다.

실행: uv run python data_client.py  (같은 폴더의 data_server.py 를 자동 실행)
"""
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 가 .env 에 없습니다"

model = ChatOpenAI(model="gpt-4o")

# MCP 서버를 subprocess(python data_server.py) 로 띄우는 파라미터
server_params = StdioServerParameters(
    command="python",
    args=["./data_server.py"],
)


async def run():
    # stdio 로 서버에 연결 → 세션 초기화
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # MCP 도구를 LangChain 도구로 로드해 ReAct 에이전트 구성
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            user_input = input("질문을 입력하세요: ")

            # 서버가 제공하는 기본 프롬프트를 불러와 메시지 구성
            prompts = await load_mcp_prompt(
                session, "default_prompt", arguments={"message": user_input}
            )
            response = await agent.ainvoke({"messages": prompts})

            print("=====RESPONSE=====")
            print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run())
