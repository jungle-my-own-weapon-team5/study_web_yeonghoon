from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("note-mcp-server")

BASE_DIR = Path("./notes")
BASE_DIR.mkdir(exist_ok=True)


def safe_title(title: str) -> str:
    """
    파일명으로 위험한 문자를 제거합니다.
    """
    title = title.strip()

    if not title:
        raise ValueError("title은 비어 있을 수 없습니다.")

    blocked = ["/", "\\", "..", ":", "*", "?", '"', "<", ">", "|"]

    for char in blocked:
        if char in title:
            raise ValueError(f"사용할 수 없는 문자가 포함되어 있습니다: {char}")

    return title


@mcp.tool
def write_note(title: str, content: str) -> str:
    """
    title과 content를 받아 로컬 notes 폴더에 메모를 저장합니다.
    기존 title이 있으면 덮어씁니다.
    """
    safe = safe_title(title)
    path = BASE_DIR / f"{safe}.txt"

    path.write_text(content, encoding="utf-8")

    return f"메모가 저장되었습니다: {safe}"


@mcp.tool
def read_note(title: str) -> str:
    """
    title에 해당하는 메모 내용을 읽어옵니다.
    """
    safe = safe_title(title)
    path = BASE_DIR / f"{safe}.txt"

    if not path.exists():
        raise FileNotFoundError(f"메모를 찾을 수 없습니다: {safe}")

    return path.read_text(encoding="utf-8")


@mcp.tool
def list_notes() -> list[str]:
    """
    notes 폴더에 저장된 메모 제목 목록을 반환합니다.
    """
    files = BASE_DIR.glob("*.txt")
    return sorted(file.stem for file in files)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )