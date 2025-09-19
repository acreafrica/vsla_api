#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class SmsOutbound(Base):
    __tablename__ = "smsoutbound"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    Request_id = sa.Column(sa.String)
    display_phone = sa.Column(sa.String)
    phone_no_id = sa.Column(sa.String)
    contact_name = sa.Column(sa.String)
    contact_wa_id = sa.Column(sa.String)
    sms_id = sa.Column(sa.String)
    type = sa.Column(sa.String)
    text_body = sa.Column(sa.String)
    replied = sa.Column(sa.Boolean, default=False)
    updated_at = sa.Column(sa.DateTime(), onupdate=datetime.now())
    created_at = sa.Column(sa.DateTime(), default=datetime.now())
