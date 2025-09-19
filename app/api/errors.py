from typing import Dict, Union
from fastapi import status

""" Construct more reusable exception classes from this
https://falcon.readthedocs.io/en/stable/api/errors.html
"""

class HTTPRequestError(Exception):
    code= 'request_error'
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *, code: str = None,  description: str = None, detail: Union[ Dict, str ] = None):
        self.detail=detail
        self.description=description or 'Request Failed!'
        self.code = code or self.code

class HTTPBadRequest(HTTPRequestError):
    code = 'bad_request'

class HTTPInvalidHeader(HTTPRequestError):
    code = 'invalid_header'

    def __init__(self, header_name: str, detail: str = None):
        message = f"The header {header_name} is invalid"
        super().__init__(message=message, detail=detail)

class HTTPMissingHeader(HTTPRequestError):
    code = 'missing_header'

    def __init__(self, header_name: str):
        message = f"The header {header_name} is missing"
        super().__init__(message=message)

class HTTPUnauthorized(HTTPRequestError):
    code = 'unauthorized'
    status_code = status.HTTP_401_UNAUTHORIZED

class HTTPForbidden(HTTPRequestError):
    code = 'forbidden'
    status_code = status.HTTP_403_FORBIDDEN


class HTTPDuplicateRecord(HTTPRequestError):
    code = 'conflict'
    status_code = status.HTTP_409_CONFLICT