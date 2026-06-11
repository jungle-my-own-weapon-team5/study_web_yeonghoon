# MCP

Model Context Protocol, or MCP, is a standard way for an AI application to expose tools and context providers to an agent. In this example, the MCP server owns the RAG search tool and the agent calls it through a JSON-RPC request.

MCP는 에이전트와 도구 사이의 연결 규약 역할을 한다. 이 예제에서 MCP 서버는 RAG 검색 도구를 가지고 있고, 에이전트는 JSON-RPC 요청으로 그 도구를 호출한다.

The useful boundary is separation of responsibilities. The agent decides when it needs external context, while the MCP server decides how to execute the tool and return structured results.

This mirrors a production setup where tools can be added, removed, permissioned, or hosted separately without rewriting the agent loop.
