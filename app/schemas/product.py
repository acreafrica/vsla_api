from typing import List, Optional
from datetime import datetime, date
#from pydantic import BaseModel
from app.schemas.base import BaseSchema
from typing import ClassVar

class ProductBase(BaseSchema):
    name: str
    sum_insured: int
   # Foreign key to PSP model
    comments: Optional[str] = None  # Optional password field for VSLA members
    require_medical_report: Optional[bool] = False
    require_invoice: Optional[bool] = False 
    require_burial_cert: Optional[bool] = False
    require_discharge_letter: Optional[bool] = False
    is_claimable: Optional[bool] = False
  
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True


class ProductCreate(ProductBase):
    pass
    


class ProductCreateOrUpdate(ProductBase):
    id: Optional[int] = None
    
class ProductDelete(BaseSchema):
    id: int


class Product(ProductBase):
    id: int
    created_at: datetime
    Updated_at: datetime

    class Config:
        from_attributes = True
