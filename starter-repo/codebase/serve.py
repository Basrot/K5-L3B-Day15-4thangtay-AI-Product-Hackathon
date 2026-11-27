"""Entrypoint for a single FastAPI worker on Railway."""

import os

import uvicorn


def main():
    port = int(os.environ.get("PORT", "8000"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT phải nằm trong khoảng 1–65535.")
    uvicorn.run("codebase.api:app", host="0.0.0.0", port=port, workers=1, limit_concurrency=8)


if __name__ == "__main__":
    main()
