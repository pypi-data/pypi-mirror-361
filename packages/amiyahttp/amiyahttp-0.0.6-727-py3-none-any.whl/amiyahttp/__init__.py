from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.staticfiles import StaticFiles

from amiyautils import snake_case_to_pascal_case, create_dir
from amiyahttp.serverBase import *
from amiyahttp.auth import *


class HttpServer(ServerABCClass, metaclass=ServerMeta):
    def __init__(self, host: str, port: int, config: ServerConfig = ServerConfig()):
        super().__init__()

        app = FastAPI(title=config.title, description=config.description, **(config.fastapi_options or {}))

        self.app = app
        self.host = host
        self.port = port
        self.config = config

        self.server = uvicorn.Server(
            config=uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                loop='asyncio',
                log_config=self.config.logging_options,
                **(self.config.uvicorn_options or {}),
            )
        )

        self.router = InferringRouter()
        self.controller = cbv(self.router)

        self.__routes = []

        @app.on_event('shutdown')
        async def on_shutdown():
            HttpServer.shutdown_all(self)

        @app.exception_handler(HTTPException)
        async def on_exception(request: Request, exc: HTTPException):
            return JSONResponse(
                self.response(code=exc.status_code, message=exc.detail),
                status_code=exc.status_code,
            )

        @app.exception_handler(RequestValidationError)
        async def on_exception(request: Request, exc: RequestValidationError):
            messages = []
            for item in exc.errors():
                messages.append(item.get('loc')[1] + ': ' + item.get('msg'))

            return JSONResponse(
                self.response(code=422, message=';'.join(messages), result=exc.errors()),
                status_code=422,
            )

    @property
    def routes(self):
        return self.__routes

    def route(self, router_path: Optional[str] = None, method: str = 'post', **kwargs):
        def decorator(fn):
            nonlocal router_path

            path = fn.__qualname__.split('.')
            c_name = snake_case_to_pascal_case(path[0][0].lower() + path[0][1:])

            if not router_path:
                router_path = f'{self.config.api_prefix}/{c_name}'
                if len(path) > 1:
                    router_path += f'/{snake_case_to_pascal_case(path[1])}'

            arguments = {
                'path': router_path,
                'tags': [c_name.title()] if len(path) > 1 else self.config.default_tags,
                **kwargs,
            }

            router_builder = getattr(self.router, method)
            router = router_builder(**arguments)

            self.__routes.append(router_path)

            return router(fn)

        return decorator

    def use_plugin(self, plugin: ServerPlugin):
        plugin.install(app=self.app, config=self.config)

    def add_static_folder(self, path: str, directory: str, **kwargs):
        create_dir(directory)
        self.app.mount(path, StaticFiles(directory=directory, **kwargs), name=directory)

    def set_index_html(self, directory: str, path: str = '/'):
        templates = Jinja2Templates(directory=directory)

        @self.app.get(path)
        async def read_root(request: Request):
            return templates.TemplateResponse('index.html', {'request': request})

    async def serve(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=['*'],
            allow_headers=['*'],
            allow_credentials=True,
        )
        self.app.include_router(self.router)

        await super().serve()

    @staticmethod
    def response(data: Any = None, code: int = 200, message: str = '', extend: Optional[dict] = None):
        return response(data, code, message, extend)
