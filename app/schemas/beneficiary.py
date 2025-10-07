from typing import List, Optional
from datetime import datetime, date
#from pydantic import BaseModel
from app.schemas.base import BaseSchema
from app.schemas.phone_validator import PhoneNumber

class BeneficiaryBase(BaseSchema):
    name: str
    phone_number: Optional[PhoneNumber] = None
    relationship_type: str
    nrc_number: str
    vsla_member_id: int
  
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True

   


class BeneficiaryCreate(BeneficiaryBase):
    pass

class Beneficiary(BeneficiaryBase):
    id: int
    created_at: datetime
    Updated_at: datetime

    class Config:
        from_attributes = True
