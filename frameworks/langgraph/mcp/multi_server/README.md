# 멀티 MCP 서버 + Supervisor (SSE)

두 MCP 서버(파일시스템 / 웹검색)를 동시에 띄우고, Supervisor 멀티에이전트가 지휘한다.

## 구성
- `file_search_server.py` — 파일 MCP 서버 (포트 8000): `file_listup`, `file_info`, `save_file`
- `web_search_server.py` — 웹 MCP 서버 (포트 8001): `web_search`, `weather_search`
- `multi_client.py` — `MultiServerMCPClient` 로 두 서버 연결 + Supervisor 그래프
- `sample.txt` — 파일 도구 테스트용 예제 파일

## 아키텍처
```
            supervisor (Router 로 다음 작업자 선택)
              /                    \
   file_searcher                web_searcher
   (file 서버 도구)              (web 서버 도구)
```

## 실행 (터미널 3개)

```bash
cp .env.example .env   # OPENAI_API_KEY, TAVILY_API_KEY 입력

cd frameworks/langgraph/mcp/multi_server

# 터미널 A — 파일 서버
uv run python file_search_server.py
# 터미널 B — 웹 서버
uv run python web_search_server.py
# 터미널 C — 클라이언트
uv run python multi_client.py
# → 질문 예: "sample.txt 의 내용을 요약해줘" / "오늘 서울 날씨 알려줘"
```

> SSE 트랜스포트라 서버 2개를 먼저 띄워둔 뒤 클라이언트를 실행해야 한다.
> 날씨 도구는 `OPENWEATHERMAP_API_KEY` 가 있을 때만 동작한다.
