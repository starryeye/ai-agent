# 데이터 분석 MCP (stdio)

CSV 통계/히스토그램/자동 모델학습 도구를 MCP 서버로 노출하고, ReAct 에이전트가 사용한다.

## 구성
- `data_server.py` — MCP 서버 (도구: `describe_column`, `plot_histogram`, `model`)
- `data_client.py` — 서버를 stdio 로 띄워 ReAct 에이전트에 연결
- `iris_data.csv` — 예제 데이터 (붓꽃)

## 실행

```bash
# 프로젝트 루트에서
cp .env.example .env   # OPENAI_API_KEY 입력 (아직 없으면)

cd frameworks/langgraph/mcp/data_analysis
uv run python data_client.py
# → 질문 입력 예: "iris_data.csv 의 species 를 예측하는 모델을 학습해줘"
#   (클라이언트가 data_server.py 를 자동으로 띄운다)
```

> stdio 트랜스포트라 서버를 따로 실행할 필요 없다. 클라이언트가 subprocess 로 서버를 띄운다.
