"""파일시스템 MCP 서버 (SSE 트랜스포트, 포트 8000).

로컬 파일 목록/정보 조회/저장 도구를 노출한다.
multi_client.py 의 supervisor 가 'file' 서버로 이 도구들을 사용한다.

실행: uv run python file_search_server.py  (백그라운드로 띄워두고 클라이언트 실행)
"""
from mcp.server.fastmcp import FastMCP
import os
import stat
import time
from typing import List

mcp = FastMCP(
    "FileSearch",
    instructions="You are a local file searching assistant.",
    host="0.0.0.0",
    port=8000,
)


@mcp.tool()
async def file_listup(directory: str) -> List[str]:
    """지정한 디렉토리의 파일 이름 목록을 반환한다."""
    try:
        return os.listdir(directory)
    except Exception as e:
        return [f"오류: {str(e)}"]


@mcp.tool()
async def file_info(path: str) -> dict:
    """파일/디렉토리의 상세 정보(내용/크기/시간/권한)를 반환한다."""
    if not os.path.exists(path):
        return {"error": f"경로 '{path}' 가 존재하지 않습니다."}
    try:
        stat_info = os.stat(path)
        file_type = "directory" if os.path.isdir(path) else "file"
        permissions = stat.filemode(stat_info.st_mode)

        content = ""
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

        return {
            "path": os.path.abspath(path),
            "content": content,
            "type": file_type,
            "size": stat_info.st_size,
            "created_time": time.ctime(stat_info.st_ctime),
            "modified_time": time.ctime(stat_info.st_mtime),
            "access_time": time.ctime(stat_info.st_atime),
            "permissions": permissions,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def save_file(content: str, output_path: str = "file_info.md") -> str:
    """주어진 내용을 지정 경로의 텍스트 파일로 저장한다."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


if __name__ == "__main__":
    # SSE 트랜스포트: HTTP(Server-Sent Events)로 통신 → 여러 서버를 각 포트로 띄울 수 있음
    mcp.run(transport="sse")
