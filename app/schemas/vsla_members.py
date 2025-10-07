from typing import List, Optional,Union
from datetime import datetime, date
from app.schemas.base import BaseSchema
from app.schemas.phone_validator import PhoneNumber
from pydantic import BaseModel,validator

class Vsla_membersBase(BaseSchema):
    member_name: str
    id_number: str
    phone_number: PhoneNumber   
    email: str
    office_position: str
    dob: date
    vsla_id: int

    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True


    @validator("dob")
    def validate_dob(cls, v: date):
        # v is guaranteed to be a `date` because of type annotation
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age > 60:
            raise ValueError("DOB indicates age above 60 years, not allowed.")
        if age < 18:
            raise ValueError("DOB indicates age below 18 years, not allowed.")
        return v
        # try:
        #     if isinstance(v, str):
        #         v = date.fromisoformat(v)  # convert from string if needed

        #     today = date.today()
        #     age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        #     if age > 60:
        #         return "DOB indicates age above 60 years, not allowed."
        #     if age < 18:
        #         return "DOB indicates age below 18 years, not allowed."

        #     return v
        # except Exception:
        #     return "Invalid DOB format"

class Vsla_membersCreate(Vsla_membersBase):
    pass

class Vsla_members(Vsla_membersBase):
    id: int
    is_admin: bool=False
    created_at: Optional[datetime] = None
    Updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True
class VslaMemberUpdate(BaseModel):
    member_name: Optional[str] = None
    id_number: Optional[str] = None
    phone_number: Optional[Union[str,int]] = None
    email: Optional[str] = None
    office_position: Optional[str] = None
    is_admin: Optional[bool] = False