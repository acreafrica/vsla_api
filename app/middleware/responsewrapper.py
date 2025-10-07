# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse
# from starlette.requests import Request
# from starlette.types import ASGIApp
# import json

# class ResponseWrapperMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app: ASGIApp):
#         super().__init__(app)

#     async def dispatch(self, request: Request, call_next):
#         # Skip docs & OpenAPI routes
#         if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
#             return await call_next(request)

#         response = await call_next(request)

#         # Read and reassemble response body
#         body = b""
#         async for chunk in response.body_iterator:
#             body += chunk

#         try:
#             content = json.loads(body)
#         except json.JSONDecodeError:
#             content = body.decode()

#         # Set wrapper values based on status code
#         success = 200 <= response.status_code < 300
#         message = (
#             "Request successful" if success
#             else content.get("detail", "Request failed") if isinstance(content, dict)
#             else "Request failed"
#         )

#         return JSONResponse(
#             content={
#                 "success": success,
#                 "message": message,
#                 "data": content if success else None,
#                 "error": None if success else content
#             },
#             status_code=response.status_code,
#         )


# class SafeResponseWrapperMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app: ASGIApp):
#         super().__init__(app)

#     async def dispatch(self, request: Request, call_next):
#         # Skip docs/OpenAPI
#         if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
#             return await call_next(request)

#         try:
#             response = await call_next(request)

#             # Handle JSONResponse differently
#             if isinstance(response, JSONResponse):
#                 try:
#                     content = json.loads(response.body)
#                 except Exception:
#                     content = {"raw": str(response.body)}
#             else:
#                 # For plain responses, read body safely
#                 body = b""
#                 async for chunk in response.body_iterator:
#                     body += chunk
#                 try:
#                     content = json.loads(body)
#                 except Exception:
#                     content = {"raw": body.decode(errors="ignore")}

#             success = 200 <= response.status_code < 300
#             message = (
#                 "Request successful" if success
#                 else content.get("message", "Request failed") if isinstance(content, dict)
#                 else str(content)
#             )

#             error_content = None
#             if not success:
#                 if isinstance(content, dict):
#                     error_content = content
#                 else:
#                     error_content = {"error": str(content)}

#             return JSONResponse(
#                 content={
#                     "success": success,
#                     "message": message,
#                     "data": content if success else None,
#                     "error": error_content
#                 },
#                 status_code=response.status_code
#             )

#         except Exception as e:
#             return JSONResponse(
#                 status_code=500,
#                 content={
#                     "success": False,
#                     "message": "Internal server error",
#                     "data": None,
#                     "error": {"type": type(e).__name__, "detail": str(e)}
#                 }
#             )
            
            

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.types import ASGIApp
import json

class SafeResponseWrapperMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip docs/OpenAPI and preflight (OPTIONS) — let CORSMiddleware handle OPTIONS
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")) or request.method == "OPTIONS":
            return await call_next(request)

        try:
            response = await call_next(request)

            # If response is not JSON (e.g., HTML, file, streaming), don't wrap — return as-is
            content_type = response.headers.get("content-type", "")
            if content_type and not content_type.startswith("application/json"):
                return response

            # Copy headers but drop content-length/transfer-encoding so they don't mismatch
            headers = {
                k: v for k, v in response.headers.items()
                if k.lower() not in ("content-length", "transfer-encoding")
            }

            # Read the body bytes (works for JSONResponse and regular responses)
            body_bytes = b""
            if getattr(response, "body", None) is not None:
                # many Starlette responses already have response.body populated
                body_bytes = response.body
            else:
                async for chunk in response.body_iterator:
                    body_bytes += chunk

            # Try to decode JSON, otherwise preserve raw text
            try:
                content = json.loads(body_bytes.decode() if isinstance(body_bytes, (bytes, bytearray)) else body_bytes)
            except Exception:
                content = {"raw": body_bytes.decode(errors="ignore")}

            success = 200 <= response.status_code < 300
            message = (
                "Request successful" if success
                else (content.get("message") if isinstance(content, dict) else "Request failed")
            )

            error_content = None
            if not success:
                error_content = content if isinstance(content, dict) else {"error": str(content)}

            return JSONResponse(
                content={
                    "success": success,
                    "message": message,
                    "data": content if success else None,
                    "error": error_content
                },
                status_code=response.status_code,
                headers=headers  # allow Starlette to set correct Content-Length
            )

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "data": None,
                    "error": {"type": type(e).__name__, "detail": str(e)}
                }
            )
