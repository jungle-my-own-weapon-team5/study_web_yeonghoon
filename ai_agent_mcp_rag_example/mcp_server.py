from __future__ import annotations

import json
import sys
from typing import Any

from rag import default_index


INDEX = default_index()


def list_tools() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "rag_search",
                "description": "Search local knowledge-base chunks and return grounded context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["query"],
                },
            }
        ]
    }


def call_tool(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name != "rag_search":
        raise ValueError(f"Unknown tool: {name}")

    query = str(arguments.get("query", ""))
    top_k = int(arguments.get("top_k", 3))
    results = INDEX.search(query=query, top_k=top_k)
    return {
        "content": [
            {
                "type": "json",
                "json": {
                    "results": [
                        {
                            "id": result.chunk.id,
                            "source": result.chunk.source,
                            "score": round(result.score, 4),
                            "text": result.chunk.text,
                        }
                        for result in results
                    ]
                },
            }
        ]
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    try:
        if method == "tools/list":
            result = list_tools()
        elif method == "tools/call":
            result = call_tool(params)
        else:
            raise ValueError(f"Unknown method: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(exc)},
        }


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        print("mcp-sever start")
        response = handle_request(json.loads(line))
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
