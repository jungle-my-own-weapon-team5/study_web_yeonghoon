# Agent

An AI agent is a loop that receives a goal, decides what information or tools it needs, calls those tools, and produces a final response. A production agent might plan multiple steps, call several tools, and ask a model to reason over the results.

AI 에이전트는 목표를 받고 필요한 정보나 도구를 고른 뒤 실행 결과를 바탕으로 응답을 만든다. 여기서는 에이전트가 MCP 서버의 RAG 검색 도구를 한 번 호출한다.

In this example, the agent performs one simple tool call. It asks the MCP server for relevant RAG chunks, then builds a grounded answer from those chunks.

The key idea is that the agent does not read local files directly. It goes through the MCP tool boundary, which makes the integration easier to test and replace.
