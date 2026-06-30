"""웹검색 MCP 서버 (SSE 트랜스포트, 포트 8001).

웹검색(Tavily) + 날씨(OpenWeatherMap) 도구를 노출한다.
multi_client.py 의 supervisor 가 'web' 서버로 이 도구들을 사용한다.

실행: uv run python web_search_server.py  (백그라운드로 띄워두고 클라이언트 실행)
필요 키: TAVILY_API_KEY (웹검색), OPENWEATHERMAP_API_KEY (날씨, 선택)
"""
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")
open_weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

mcp = FastMCP(
    "WebSearch",
    instructions="You are a web search assistant.",
    host="0.0.0.0",
    port=8001,
)


@mcp.tool()
async def web_search(query: str, topic: str = "general", max_results: int = 3) -> str:
    """주어진 쿼리로 웹을 검색해 결과를 반환한다.

    Args:
        query (str): 검색어
        topic (str): "general"(기본) 또는 "news"
        max_results (int): 반환할 결과 수 (기본 3)
    """
    url = "https://api.tavily.com/search"
    payload = {
        "query": query,
        "topic": topic,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": True,
    }
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.text


@mcp.tool()
async def weather_search(city: str) -> dict:
    """도시의 현재/일별 날씨와 개요를 반환한다 (OpenWeatherMap).

    Args:
        city (str): 날씨를 조회할 도시 이름
    """
    def get_coordinates(city, api_key):
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        data = requests.get(url).json()
        if not data:
            raise ValueError(f"도시 '{city}' 정보를 찾을 수 없습니다.")
        return data[0]["lat"], data[0]["lon"]

    lat, lon = get_coordinates(city, open_weather_api_key)
    data = json.loads(requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&lang=kr&appid={open_weather_api_key}"
    ).text)
    overview = json.loads(requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon={lon}&appid={open_weather_api_key}"
    ).text)
    return {
        "current_weather": data.get("current"),
        "daily_weather": data.get("daily"),
        "weather_overview": overview.get("weather_overview"),
    }


if __name__ == "__main__":
    mcp.run(transport="sse")
