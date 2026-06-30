# MCP (Model Context Protocol) 예제

**MCP** 는 LLM 에이전트가 외부 "도구 서버"를 **표준 프로토콜**로 연결해 쓰는 방식이다.
도구 구현(서버)과 사용(클라이언트)을 분리할 수 있어, 같은 서버를 여러 에이전트/앱에서 재사용한다.

`langchain-mcp-adapters` 가 MCP 도구를 LangChain/LangGraph 도구로 변환해준다.

## 폴더

| 폴더 | 내용 | 트랜스포트 |
|---|---|---|
| `data_analysis/` | 단일 MCP 서버(데이터 분석) + ReAct 클라이언트 | stdio |
| `multi_server/` | 멀티 MCP 서버(파일 + 웹) + Supervisor 클라이언트 | SSE |

## 트랜스포트 차이

- **stdio**: 클라이언트가 서버 스크립트를 subprocess 로 띄워 표준입출력으로 통신.
  서버를 따로 실행할 필요 없이 클라이언트만 돌리면 된다. (`data_analysis`)
- **SSE**: 서버를 HTTP 포트로 띄워두고 클라이언트가 URL 로 접속.
  여러 서버를 각 포트로 동시에 띄울 수 있다. (`multi_server`)

각 폴더의 README 를 참고해 실행한다.
