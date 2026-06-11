# AI Agent + MCP + RAG Example

Small, dependency-light example showing how an AI agent can call an MCP-style tool server to retrieve grounded context from local documents.

The default agent is intentionally local and deterministic, so the project works without API keys or network access. You can later replace `LocalAnswerModel` with an LLM call while keeping the MCP/RAG boundary intact.

## Architecture

```text
User question
    |
    v
agent.py
    |
    | JSON-RPC request: tools/call -> rag_search
    v
mcp_server.py
    |
    v
rag.py -> data/*.md
    |
    v
Retrieved chunks -> grounded answer
```

## Files

- `agent.py`: CLI agent that asks the MCP server for relevant context and writes an answer.
- `mcp_server.py`: minimal MCP-style JSON-RPC server over stdio.
- `rag.py`: document loading, chunking, indexing, and keyword scoring.
- `data/`: sample knowledge base documents.
- `tests/test_rag.py`: quick regression test for retrieval.

## Run

From this directory:

```bash
python3 agent.py "MCP는 이 예제에서 어떤 역할을 해?"
```

Example output:

```text
Answer:
MCP는 에이전트와 검색 도구 사이의 표준화된 연결 계층 역할을 합니다...

Sources:
- data/mcp.md#chunk-1
```

## Inspect The MCP Server

List tools:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n' | python3 mcp_server.py
```

Call the RAG tool:

```bash
printf '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"rag_search","arguments":{"query":"agent rag mcp","top_k":2}}}\n' | python3 mcp_server.py
```

## Test

```bash
python3 -m unittest discover tests
```

## Swap In A Real LLM

`agent.py` has a `LocalAnswerModel` class. Replace its `answer()` method with a call to your preferred model:

1. Keep the retrieved chunks as the only trusted context.
2. Ask the model to cite chunk IDs.
3. Keep the MCP request shape unchanged.

That keeps the example close to production architecture: the model reasons, the MCP tool fetches, and RAG grounds the response.
