from typing import List, Optional
from datetime import datetime, date
from app.schemas.base import BaseSchema
#from pydantic import BaseModel

class VslaBase(BaseSchema):
    vsla_group_name: str
    expected_membership_number: Optional[int] = 0
    country: str
    province: str
    district: str
    ward: str
    vsla_status: str
    psp_id: int  # Foreign key to PSP model
    password: Optional[str] = None  # Optional password field for VSLA members
  
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True


class VslaCreate(VslaBase):
    pass

class Vsla(VslaBase):
    id: int
    created_at: datetime
    Updated_at: datetime

    class Config:
        from_attributes = True
