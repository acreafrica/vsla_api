from pydantic import BaseModel
from datetime import date, datetime

class BaseSchema(BaseModel):
    class Config:
        # orm_mode = True   # ✅ allow parsing from ORM objects
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y/%m/%d") if v else None
        }
