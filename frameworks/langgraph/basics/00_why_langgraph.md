# 왜 LangGraph 인가

이 폴더의 다른 노트북으로 들어가기 전, "LangGraph가 뭐고 왜 이것을 쓰는가"를 정리한다.

## 1. LangGraph 정의

**LangGraph** 는 다양한 워크플로우 및 에이전트 시스템을 설계하기 위한 프레임워크다.
가장 큰 특징은 **애플리케이션의 로직을 노드(Node)와 엣지(Edge)로 구성된 그래프로 표현**한다는 점이다.

공식 사이트: <https://www.langchain.com/langgraph>

## 2. Graph 라는 모델

수학적 의미의 그래프는 **꼭짓점(노드, Node) 의 집합 + 그 노드들을 잇는 변(엣지, Edge) 의 집합**으로 정의된다.
LangGraph 에서는 이 추상을 다음과 같이 매핑한다.

| 그래프 요소 | LangGraph 의미 |
|---|---|
| **Node** | 하나의 실행 단위 (보통 파이썬 함수) |
| **Edge** | 실행 흐름의 경로 — 어느 노드 다음에 어느 노드로 갈지 |

즉, 에이전트의 동작이 곧 "그래프를 따라가는 순회(traversal)" 가 된다.

## 3. 왜 그래프로 에이전트를 관리하는가

LLM 기반 에이전트의 흐름은 단순한 선형(체인) 으로 끝나지 않는다.

- 도구를 호출 → 결과를 보고 → 다시 LLM에 물어볼지 종료할지 결정 (**루프**)
- 사용자 의도에 따라 다른 경로로 분기 (**조건부 라우팅**)
- 여러 에이전트가 협업/병렬 실행 (**다중 노드 동시 실행**)
- 중간에 사람이 끼어들어 승인/수정 (**human-in-the-loop**)

이런 흐름을 코드 if/else로 박아두면 수정이 어렵고 시각화가 안 된다.
**그래프로 명시하면** — 분기/루프/병렬을 데이터 구조로 다룰 수 있고, 시각화도 자동으로 나오며, 중간 상태 저장(checkpointing)과 재개도 가능해진다.

## 4. LangChain vs LangGraph

같은 LangChain 생태계 안의 두 추상이지만 결이 다르다.

|  | LangChain | LangGraph |
|---|---|---|
| 모델 | **체인(Chain)** — 직선 흐름 | **그래프(Graph)** — 분기·루프·병렬 가능 |
| 유연성 | 중간 | 높음 |
| 전형 사용처 | 간단한 RAG, 단발성 프롬프트 파이프라인 | 복잡한 에이전트, 다중 에이전트 시스템 |

둘은 경쟁 관계가 아니라 **레이어**다 — LangGraph 노드 안에서 LangChain Runnable을 자유롭게 쓸 수 있다.

## 5. LangGraph 를 사용해야 하는 4가지 이유

1. **복잡한 AI Agent 로직 구현** — 여러 단계의 워크플로우를 그래프로 자연스럽게 그릴 수 있다.
2. **확장성 높은 사용자 커스텀 로직** — 원하는 흐름을 노드/엣지로 단계별 구성 가능.
3. **그래프 분기 처리를 통한 유연한 제어** — 조건부 엣지로 런타임에 경로를 정한다.
4. **양방향 파이프라인 구성을 통한 성능 개선** — 이전 단계로 돌아가 결과의 방향성·품질을 개선 (reflect, retry 패턴).

## 6. 대표 패턴 예시

LangGraph로 흔히 만드는 시스템들:

- **Tool-using Agent** — `START → Agent → (도구 호출) → Agent → END` 루프
- **Reflect (Generate / Critique 루프)** — N번 반복하며 출력 품질을 다듬는다
- **GraphRAG with Cypher** — 질의 → Cypher 생성 → DB 실행 → (오류 시) 쿼리 수정 → 답변
- **Plan & Execute** — Planner가 계획을 세우고, 실행 에이전트가 한 단계씩 처리 후 계획 재수립

이들은 모두 "분기·루프·다중 상태"가 본질이라 체인으로 표현하기 어렵다.

## 7. LangGraph 의 핵심 구성요소

세 개로 정리된다. 다음 노트북부터 이 셋을 차례로 다룬다.

| 요소 | 한 줄 정의 | 일반적 구현 |
|---|---|---|
| **State (상태)** | Agent의 현재 상태를 나타내는 데이터 구조 | `TypedDict`, Pydantic `BaseModel` |
| **Nodes (노드)** | Agent가 수행하는 논리를 구현하는 함수 | 현재 State를 받아 업데이트된 State를 반환 |
| **Edges (엣지)** | 다음에 실행될 경로를 결정하는 함수 | 기본 엣지 / 조건부 엣지 |

여기에 더해 **Reducer (리듀서)** — 같은 State 필드를 여러 노드가 갱신할 때 어떻게 합칠지의 규칙 — 까지 알면 LangGraph 기초의 9할이다.

### 잠깐: `TypedDict` 와 Pydantic `BaseModel` 이 뭔가?

State 를 정의할 때 위 두 가지가 등장한다. 둘 다 **"딕셔너리(dict)에 정해진 모양을 부여하는" 도구**다.
파이썬 `dict` 는 아무 키나 아무 타입이나 넣을 수 있어 자유롭지만, "이 데이터는 반드시 이런 키/타입을 가져야 한다"는 약속을 강제하지 못한다. 그 약속을 미리 선언하는 것이 이 둘이다.

| | `TypedDict` | Pydantic `BaseModel` |
|---|---|---|
| 출신 | **파이썬 표준** (`typing` 모듈, 설치 불필요) | **외부 라이브러리** (`pydantic`) |
| 실체 | 그냥 dict | 클래스 인스턴스(객체) |
| 값 접근 | `state["name"]` | `state.name` |
| 잘못된 타입을 넣으면? | **그냥 통과** (IDE/타입검사기만 경고) | **런타임에 `ValidationError` 로 막음** |
| 무게 | 매우 가벼움 | 약간 무거움 |

```python
from typing import TypedDict        # 파이썬 표준
class UserTD(TypedDict):
    id: int
    name: str

from pydantic import BaseModel      # 외부 라이브러리
class UserPyd(BaseModel):
    id: int
    name: str
```

> `class UserTD(TypedDict):` 의 **소괄호는 상속**을 뜻한다 (생성자 파라미터가 아니다).
> 파이썬에서 `class 이름(부모):` 형태의 괄호는 "어떤 부모 클래스를 물려받는가"를 적는 자리다.
> 정의할 때 괄호(상속)와, 인스턴스를 만들 때 괄호(`UserTD(id=1, name="철수")`, 값 전달)는 의미가 다르다.

→ 빠른 프로토타이핑이면 `TypedDict`, 외부 입력 검증이 중요하면 Pydantic.
실제 코드와 차이는 다음 노트북 `01_state_node_graph.ipynb` 에서 직접 다룬다.

다음: `01_state_node_graph.ipynb` 에서 위 셋을 코드로 직접 다뤄본다.
