# RAG, MCP, AI Agent 공식 문서 정리

## 한 줄 구분

| 주제 | 의미 |
| --- | --- |
| RAG | 모델이 답변하기 전에 문서, DB, 검색 결과 등에서 관련 정보를 찾아 참고하는 패턴 |
| MCP | AI 앱이나 Agent가 외부 도구, 파일, DB, API와 연결되는 표준 프로토콜 |
| AI Agent | 모델이 도구 호출, 판단, 반복 작업, 위임 등을 하며 목표를 수행하는 구조 |

## 공식 문서

| 주제 | 공식 문서 |
| --- | --- |
| RAG | [OpenAI Help Center - RAG and semantic search](https://help.openai.com/en/articles/8868588-retrieval-augmented-generation-rag-and-semantic-search-for-gpts%3F.midi) |
| MCP | [Model Context Protocol - Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture) |
| MCP Spec | [Model Context Protocol - Specification](https://modelcontextprotocol.io/specification/2024-11-05/basic) |
| AI Agent | [OpenAI Platform - Agents SDK](https://platform.openai.com/docs/guides/agents-sdk/) |
| Python Agent SDK | [OpenAI Agents SDK Python](https://openai.github.io/openai-agents-python/agents/) |
| JavaScript Agent SDK | [OpenAI Agents SDK JavaScript](https://openai.github.io/openai-agents-js/guides/agents/) |

## 공부 순서 추천

1. RAG 개념을 먼저 본다.
2. OpenAI Agents SDK로 Agent 구조를 본다.
3. MCP Architecture 문서로 Agent와 외부 도구가 연결되는 방식을 본다.
4. MCP 서버나 클라이언트를 직접 만들 때 MCP Specification을 본다.

## 용어 메모

MCS라고 말하는 경우가 있지만, AI Agent나 도구 연결 문맥에서는 보통 MCP, 즉 Model Context Protocol을 의미하는 경우가 많다.

