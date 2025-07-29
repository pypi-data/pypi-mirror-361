import abc

from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from amiyautils import random_code
from amiyahttp.serverBase import ServerPlugin, ServerConfig, response


class OAuth2(ServerPlugin):
    def __init__(
        self,
        secret_key: str = '',
        access_token_expire_minutes: int = 60,
        token_url: str = 'token',
        algorithm: str = 'HS256',
    ):
        self.secret_key = secret_key or random_code(16)
        self.access_token_expire_minutes = access_token_expire_minutes
        self.token_url = token_url
        self.algorithm = algorithm

        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @abc.abstractmethod
    async def get_user_password(self, username: str) -> str:
        raise NotImplementedError

    def authorized_user(self) -> str:
        return Depends(self.current_user())

    def authenticate_user(self, password_str: str, password: str):
        return self.pwd_context.verify(password_str, password)

    def create_password(self, password: str):
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def current_user(self):
        async def cu(token: str = Depends(self.oauth2_scheme)):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={
                    'WWW-Authenticate': 'Bearer',
                },
            )
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                username: str = payload.get('sub')
                if username is None:
                    raise credentials_exception
            except JWTError:
                raise credentials_exception
            return username

        return cu

    def install(self, app: FastAPI, config: ServerConfig):
        @app.post(f'{config.api_prefix}/token', tags=config.default_tags)
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            user_password = await self.get_user_password(form_data.username)
            if not user_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Cannot get user password by username: {form_data.username}',
                )

            if not self.authenticate_user(form_data.password, user_password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')

            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = self.create_access_token(
                data={'sub': form_data.username},
                expires_delta=access_token_expires,
            )
            return response(
                extend={
                    'access_token': access_token,
                    'token_type': 'bearer',
                }
            )
