#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
def utc_now():
    return datetime.now(timezone.utc)

class Vsla_members(Base):
    __tablename__ = "vsla_members"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    member_name = sa.Column(sa.String)
    id_number = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    email = sa.Column(sa.String)
    office_position = sa.Column(sa.String)
    dob = sa.Column(sa.String)
    is_admin = sa.Column(sa.Boolean, default=False)
    address = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now,onupdate=utc_now)
    # ✅ ForeignKey to Vsla
    vsla_id = sa.Column(sa.Integer, sa.ForeignKey("vsla.id"))

    # ✅ Many-to-One: Vsla_members → Vsla
    vsla = relationship("Vsla", back_populates="members")
    password_data = relationship("VslaPassword", uselist=False, back_populates="vsla", cascade="all, delete")
    password_resets = relationship("VslaPasswordReset", uselist=False, back_populates="vsla", cascade="all, delete")
    membercontributions = relationship("Vsla_member_contributions", uselist=False, back_populates="vsla_member", cascade="all, delete")
    claims = relationship("claims", back_populates="member", cascade="all, delete-orphan")
    beneficiaries = relationship("Beneficiary", back_populates="vsla_member", cascade="all, delete")