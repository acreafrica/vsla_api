from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

class smsinboundBase(BaseModel):
    Request_id: str
    display_phone: str
    phone_no_id: str
    contact_name: str
    contact_wa_id: str
    sms_id: str
    type: str
    text_body: str
    replied: bool=False
    list_reply_id : Optional[str]
    reply_tittle : Optional[str]
    reply_description : Optional[str]
    #created_at: Optional[datetime] Optional[str]
    class Config:
        arbitrary_types_allowed = True

class smsinboundCreate(smsinboundBase):
    pass

class SmsInbound(smsinboundBase):
    id: int

    class Config:
        orm_mode = True
