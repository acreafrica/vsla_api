from typing import List, Optional
from datetime import datetime, date
from app.schemas.base import BaseSchema
#from pydantic import BaseModel

class Vsla_members_contributionsBase(BaseSchema):
    vsla_member_id: int
    month: str
    year: str
    amount: int
   
  
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True


class Vsla_members_contributionsCreate(Vsla_members_contributionsBase):
    pass

class Vsla_members_contributions(Vsla_members_contributionsBase):
    id: int
    created_at: Optional[datetime] = None
    Updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

