"""Bound each request body before JSON or multipart parsing."""

from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes=11 * 1024 * 1024):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            declared = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await JSONResponse({"detail": "Content-Length không hợp lệ."}, status_code=400)(scope, receive, send)
        if declared > self.max_bytes:
            return await self._reject(scope, receive, send)
        chunks, length = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            part = message.get("body", b"")
            length += len(part)
            if length > self.max_bytes:
                return await self._reject(scope, receive, send)
            chunks.append(part)
            if not message.get("more_body", False):
                break
        body = b"".join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay, send)

    async def _reject(self, scope, receive, send):
        response = JSONResponse({"detail": "Yêu cầu vượt giới hạn 11 MB."}, status_code=413)
        await response(scope, receive, send)
