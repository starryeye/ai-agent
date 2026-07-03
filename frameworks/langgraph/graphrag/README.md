# GraphRAG — 지식 그래프 기반 RAG

문서 청크가 아니라 **그래프(노드/관계)** 에서 정보를 검색하는 RAG. "A 와 함께 출연한 배우",
"이 사건을 수사한 경관" 같은 **관계형 질문**에 강하다. 그래프 DB 로 **Neo4j** 를 쓴다.

## 노트북

| 노트북 | 방식 | 핵심 |
|---|---|---|
| `01_vector_graphrag` | 벡터 검색 | `VectorRetriever`, `SimpleKGPipeline`(PDF→KG 자동구축) |
| `02_graph_text2cypher` | 그래프 검색 | `Text2CypherRetriever` (자연어→Cypher) |
| `03_vector_plus_graph` | 결합 | `VectorCypherRetriever` (벡터로 찾고 관계로 확장) |
| `04_graphrag_agent` | **LangGraph Agent** | Text2Cypher 자가교정 (생성→검증→수정→실행→평가) |

01~03 은 `neo4j-graphrag` 라이브러리 사용법, **04 는 LangGraph 로 직접 구현**한 GraphRAG 에이전트다
(앞서 배운 SQL RAG 의 그래프DB 버전).

## Neo4j 준비 (필수)

이 노트북들은 **Neo4j 인스턴스**가 있어야 실행된다. SQLite 처럼 파일 하나로 되지 않는다.
세 가지 방법 중 하나:

1. **Neo4j Aura (클라우드, 무료 티어)** — 가장 간단
   - <https://neo4j.com/product/auradb/> 에서 무료 인스턴스 생성
   - 접속 URI(`neo4j+s://...`)·비밀번호를 `.env` 에 입력
2. **로컬 Docker**
   ```bash
   docker run -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your-password neo4j:latest
   # URI: neo4j://localhost:7687
   ```
3. **Neo4j Desktop** 설치 후 로컬 DB 생성

### 예제 데이터셋
- 영화 그래프(`Person-ACTED_IN->Movie-IN_GENRE->Genre`): `04`, `03` 에서 사용
  - Neo4j 예제: <https://github.com/neo4j-graph-examples/recommendations>
- 03/01 의 벡터 검색은 노드에 임베딩 속성이 미리 있어야 한다
  (`SimpleKGPipeline` 로 문서에서 자동 구축하거나, 예제 데이터셋 로드)

## 실행

```bash
cp .env.example .env   # NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD / OPENAI_API_KEY 입력
```
그다음 노트북을 위→아래로 실행. Neo4j 연결이 안 되면 첫 연결 셀에서 에러가 난다.

## 정리 — RAG 스펙트럼
- 문서: **RAG** (벡터 검색) → `frameworks/langgraph/rag/`
- 관계형 DB: **SQL RAG** (Text-to-SQL) → `rag/05_sql_rag`
- 지식 그래프: **GraphRAG** (Text2Cypher) → 여기

세 경우 모두 "외부 지식을 근거로 답하고, 품질을 검증·교정" 하는 것이 핵심이다.
