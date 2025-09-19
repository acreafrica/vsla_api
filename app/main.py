from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.middleware.responsewrapper import  SafeResponseWrapperMiddleware

from app.core.config import settings
from app.api.v1.api import router
from datetime import date, datetime
from fastapi.encoders import jsonable_encoder

from fastapi.openapi.utils import get_openapi

from app.api.errors import HTTPRequestError

#from app.database.redis_client import redis_client
from fastapi.middleware.cors import CORSMiddleware
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        encoders = {
            date: lambda v: v.strftime("%Y/%m/%d"),
            datetime: lambda v: v.strftime("%Y/%m/%d")
        }
        return super().render(
            jsonable_encoder(content, custom_encoder=encoders)
        )

# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)#,default_response_class=CustomJSONResponse )
#     app.include_router(router)
#     app.docs_url="/docs",       # Swagger UI
#     app.redoc_url="/redoc",     # ReDoc
#     app.openapi_url="/openapi.json"
#     #application.add_event_handler("startup", create_redis_pool)
#     #application.add_event_handler("shutdown", close_redis_pool)
#     return app
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        docs_url="/docs",        # Swagger UI will be /vslaapi/docs
        redoc_url="/redoc",      # ReDoc will be /vslaapi/redoc
        openapi_url="/openapi.json",
        #root_path="/vslaapi"     # <-- important!
    )
    app.include_router(router)
    return app


app = create_app()


app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],#settings.ALLOWED_ORIGINS, 
    allow_methods=["*"], 
    allow_headers=["*"], 
    allow_credentials=True 
    )
#app.add_middleware(ResponseWrapperMiddleware)
app.add_middleware(SafeResponseWrapperMiddleware)
@app.on_event("startup")
async def startup():
    pass
    #redis_client.start(6379)
    

@app.exception_handler(HTTPRequestError)
async def bad_request_exception_handler(request: Request, exc: HTTPRequestError):
    return JSONResponse(
        status_code=exc.status_code or 400,
        content={
            'code': exc.code,
            'description': exc.description,
            'detail': exc.detail
        }
    )