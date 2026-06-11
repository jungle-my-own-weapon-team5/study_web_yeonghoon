# Food Test 구현 명세

## 1. 서비스 개요

Food Test는 식단 사진 분석 Agent와 기본 게시판 기능을 함께 제공하는 서비스입니다.

사용자는 음식 사진이나 식사 설명을 등록할 수 있고, Agent는 음식 종류와 대략적인 양을 추정해 하루 영양 기록에 반영합니다. 사용자는 게시판을 통해 식단 기록, 질문, 팁을 Markdown 게시글로 공유할 수 있습니다.

## 2. 핵심 기능

### 2.1 식단 사진 분석 + 하루 영양 리포트 Agent

사용자가 음식 사진 또는 식사 설명을 입력하면 Agent는 다음 흐름으로 처리합니다.

1. 입력이 음식 관련 사진/텍스트인지 판단합니다.
2. 음식 종류와 대략적인 섭취량을 추정합니다.
3. RAG로 음식별 영양 정보와 주의점을 검색합니다.
4. MCP 도구를 통해 식단 기록 DB에 저장합니다.
5. 하루 누적 칼로리, 단백질, 나트륨, 당류, 포화지방 위험도를 계산합니다.
6. 오늘 남은 식사 방향을 제안합니다.

예시 입력:

```text
오늘 점심 이거 먹었어
```

예시 응답:

```json
{
  "meal": "lunch",
  "estimated_calories": "약 650 kcal",
  "warning": "나트륨이 높을 수 있으므로 저녁은 국물류와 짠 반찬을 줄이는 것이 좋습니다.",
  "saved": true
}
```

### 2.2 기본 게시판 기능

- 회원가입: 이메일, 비밀번호, 닉네임을 사용합니다.
- 기본 닉네임: `익명0000` 형식이며 숫자는 중복되지 않아야 합니다.
- 닉네임은 중복될 수 없습니다.
- 로그인은 JWT 기반으로 구현합니다.
- 로그아웃 기능을 제공합니다.
- 게시글 CRUD를 구현합니다.
- 게시글 에디터는 Markdown 포맷으로 최소 구현합니다.
- 댓글 목록은 일정 개수 이상일 때 `view more` 버튼으로 추가 로드합니다.
- 게시글에는 `#태그명` 형식의 태그를 붙일 수 있습니다.
- 게시글 목록은 페이지네이션을 지원합니다.
- 검색은 게시글 제목 기준으로 지원합니다.

## 3. AI 구성

### 3.1 AI Agent

AI Agent는 사용자 요청을 해석하고 필요한 도구를 선택합니다.

- 음식 사진 또는 식사 텍스트인지 판단합니다.
- 음식 종류와 양을 추정합니다.
- RAG 검색이 필요한 경우 MCP의 `rag_search` 도구를 호출합니다.
- DB 저장이나 하루 기록 조회가 필요한 경우 MCP 도구를 호출합니다.
- 도구 결과와 사용자 질문을 바탕으로 최종 답변을 생성합니다.

### 3.2 RAG

RAG는 Agent가 답변에 사용할 근거 정보를 검색합니다.

검색 대상:

- 음식별 칼로리 및 영양 정보
- 나트륨, 당류, 포화지방 기준
- 다이어트 식단 가이드
- 건강 주의사항
- 일반적인 음식량 추정 기준

RAG 검색 결과는 최종 답변이 아니라, LLM이 답변을 생성할 때 사용하는 근거 context입니다.

### 3.3 pgvector

pgvector는 RAG용 문서 chunk embedding을 저장하고 유사도 검색을 수행합니다.

- 음식/영양 문서를 chunk 단위로 저장합니다.
- 각 chunk의 embedding vector를 저장합니다.
- 사용자 질문 embedding과 가장 유사한 chunk를 검색합니다.
- 검색 결과는 score, source, text, metadata를 포함합니다.

### 3.4 MCP

MCP는 Agent가 사용할 수 있는 도구를 표준화해서 제공합니다.

필수 도구:

- `rag_search(query, top_k)`: 음식/영양 관련 문서 검색
- `save_meal_log(date, meal, foods, nutrition)`: 식단 기록 저장
- `get_today_nutrition(date)`: 하루 누적 영양 정보 조회
- `update_weight_log(date, weight)`: 체중 기록 저장
- `create_warning_note(date, message, severity)`: 주의사항 기록
- `create_post(title, body, tags)`: 게시글 생성
- `search_posts(title, page)`: 게시글 제목 검색

## 4. 프로젝트 구조

```text
food_test/
  README.md
  AGENT.MD
  frontend/
  backend/
```

백엔드는 유지보수 가능한 모듈 단위로 구현합니다. 프론트엔드는 재사용 가능한 컴포넌트 단위로 구현합니다.

## 5. 기술 스택

- Frontend: React + TypeScript + Vite
- Frontend state: Zustand
- Backend: Python FastAPI
- Database: PostgreSQL + pgvector
- Hosting DB: Supabase
- AI orchestration: LangChain
- Auth: JWT

환경 변수는 `.env`로 관리하며, `.env`는 `.gitignore`에 포함합니다.

## 6. 구현 시 주의사항

- 음식 사진 분석 결과는 추정값이므로 확정적인 의학/영양 진단처럼 표현하지 않습니다.
- 건강 관련 답변은 일반적인 참고 정보로 제공하고, 질병/치료 판단은 전문가 상담을 권장합니다.
- RAG 검색 결과가 부족하면 근거가 부족하다고 안내합니다.
- 사용자의 식단/체중 정보는 민감 정보로 취급합니다.
- Agent는 DB를 직접 조작하지 않고 MCP 도구를 통해 필요한 작업을 수행합니다.
