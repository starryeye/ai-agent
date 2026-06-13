# ai-agent

AI Agent 학습 전반을 담는 개인 학습 레포.
LangGraph는 그 안의 한 프레임워크일 뿐, 다른 프레임워크/주제도 함께 다룬다.

## 디렉토리 구조

```
ai-agent/
├── frameworks/        # 프레임워크별 학습 (langgraph, langchain, ...)
│   └── langgraph/
│       ├── basics/    # 기초 개념 노트북 (State, Node, Edge, Reducer) — LLM 불필요
│       ├── projects/  # 입문 프로젝트 (챗봇, Tool Calling, Structured Output 등) — LLM 사용
│       └── patterns/  # 에이전트 패턴 (Reflection, Plan&Execute, 코드수정 루프 등)
├── concepts/          # 프레임워크 무관 개념 (agent-patterns, rag, graphrag, ...)
├── projects/          # 프레임워크/주제 통합 프로젝트
└── notes/             # 자유 학습 노트, 논문 정리
```

## 환경

- Python **3.11**
- 패키지 매니저: [**uv**](https://docs.astral.sh/uv/)
- IDE: PyCharm Pro (Jupyter / FastAPI 지원)

## 시작하기

```bash
# 1) 의존성 동기화 — .venv 자동 생성
uv sync

# 2) Jupyter Lab 실행
uv run jupyter lab

# 3) (선택) API 키가 필요한 노트북을 다루기 전 .env 작성
cp .env.example .env
```

### PyCharm 인터프리터 연결
`Settings → Project → Python Interpreter → Add Interpreter → Select existing`
→ `/Users/starryeye/study/ai-agent/.venv/bin/python`
