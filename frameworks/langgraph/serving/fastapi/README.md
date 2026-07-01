# FastAPI 로 LangGraph 에이전트 서빙하기

노트북에서 실험하던 LangGraph 에이전트를 **API 서버로 배포** 하는 단계.
FastAPI(웹 프레임워크) + uvicorn(ASGI 서버) 조합.

## 파일
- `basics.py` — FastAPI 기초 (GET/POST/PUT/DELETE 라우팅). LangGraph 없음
- `main.py` — LangGraph 웹스크래핑 에이전트를 API 로 노출 (`/ai-assist/invoke`, `/ai-assist/stream`)
- `client_test.ipynb` — 서버를 띄운 뒤 클라이언트로 호출 테스트

## 실행

```bash
cp .env.example .env   # OPENAI_API_KEY 입력

cd frameworks/langgraph/serving/fastapi

# 기초 서버 (LangGraph 없이 FastAPI 감 잡기)
uv run uvicorn basics:app --reload

# 에이전트 서버
uv run uvicorn main:app --reload
```

- 서버 문서(Swagger UI): <http://127.0.0.1:8000/docs>
- 서버를 띄운 뒤 `client_test.ipynb` 로 호출 테스트

## invoke vs stream
| 엔드포인트 | 방식 | 반환 |
|---|---|---|
| `POST /ai-assist/invoke` | 동기 단발 | 최종 답변 JSON |
| `GET /ai-assist/stream` | SSE 스트리밍 | 노드별 진행 실시간 |

> `uvicorn main:app` 에서 `main` 은 파일명(main.py), `app` 은 그 안의 FastAPI 인스턴스.
> `--reload` 는 코드 변경 시 서버 자동 재시작 (개발용).
