from pydantic import BaseModel, EmailStr
class PspLogin(BaseModel):
    phone: str# was using email
    password: str

class vslaLogin(BaseModel):
    phone: str
    password: str

class ResetPasswordRequest(BaseModel):
    phone: str

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str


class VslaResetRequest(BaseModel):
    phone: str

class VslaResetConfirm(BaseModel):
    token: str
    new_password: str
