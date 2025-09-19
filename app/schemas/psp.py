from typing import List, Optional
from datetime import datetime, date
from app.schemas.base import BaseSchema
from app.schemas.phone_validator import PhoneNumber
#from pydantic import BaseModel

class pspBase(BaseSchema):
    first_name: str
    last_name: str
    email: Optional[str]
    gender: str
    phone_number: PhoneNumber
    address: str
    country: str
    id_copy: Optional[str]=""
    professional_cert: Optional[str]=""
    #password : Optional[str]=""
    phone_validated : bool=False
    comments : Optional[str]=""
    approval_status : Optional[str]="pending"  # Default status can be "pending", "approved", "rejected"
    #password: Optional[str] = None  # Optional password field for PSP members
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True

class pspCreate(pspBase):
    password: str
    #pass

class psp(pspBase):
    id: int
    created_at: Optional[datetime] = None
    Updated_at: Optional[datetime] = None
    is_admin: bool=False

    class Config:
        orm_mode = True
