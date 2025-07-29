from typing import Callable, List, Optional
from fastapi import FastAPI, Request, Response
from amiyahttp.serverBase import ServerPlugin, ServerConfig


class AuthKey(ServerPlugin):
    def __init__(self, auth_key: str, headers_key: str = 'Authorization', allow_path: Optional[List[str]] = None):
        self.auth_key = auth_key
        self.headers_key = headers_key
        self.allow_path = allow_path or []

    def install(self, app: FastAPI, config: ServerConfig):
        @app.middleware('http')
        async def interceptor(request: Request, call_next: Callable):
            results = []

            for path in ['/docs', '/favicon.ico', '/openapi.json', *self.allow_path]:
                if not request.scope['path'].startswith(path):
                    if request.headers.get(self.headers_key) != self.auth_key:
                        results.append(False)
                        continue
                results.append(True)

            if not any(results):
                return Response('Invalid authKey', status_code=401)

            return await call_next(request)
        
    def add_allow_path(self, path: str):
        if path not in self.allow_path:
            self.allow_path.append(path)
