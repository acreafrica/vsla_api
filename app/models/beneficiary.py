#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class Beneficiary(Base):
    __tablename__ = "beneficiary"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    relationship_type = sa.Column(sa.String)
    nrc_number = sa.Column(sa.String)
    vsla_member_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"))
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now,onupdate=utc_now)

    vsla_member = relationship("Vsla_members", back_populates="beneficiaries")


  
   