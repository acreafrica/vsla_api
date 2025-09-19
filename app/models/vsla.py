#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class Vsla(Base):
    __tablename__ = "vsla"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    vsla_group_name = sa.Column(sa.String)
    expected_membership_number = sa.Column(sa.Integer)
    country = sa.Column(sa.String)
    province = sa.Column(sa.String)
    district = sa.Column(sa.String)
    ward = sa.Column(sa.String)
    vsla_status = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now,onupdate=utc_now)

    members = relationship("Vsla_members", back_populates="vsla", cascade="all, delete")
    psp_id = sa.Column(sa.Integer, sa.ForeignKey("pspmodel.id"))  # FK to PSP
    psp = relationship("PspModel", back_populates="vsla_groups")
    #vslacontributions = relationship("Vsla_contributions", back_populates="vsla_contributions", cascade="all, delete")
    
    contributions = relationship("Vsla_contributions", back_populates="vsla", cascade="all, delete")