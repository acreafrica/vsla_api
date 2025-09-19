#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class PspModel(Base):
    __tablename__ = "pspmodel"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    email = sa.Column(sa.String)
    gender = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    address = sa.Column(sa.String)
    country = sa.Column(sa.String)
    id_copy = sa.Column(sa.String, nullable=True)
    professional_cert = sa.Column(sa.String, nullable=True)
    password = sa.Column(sa.String)
    phone_validated = sa.Column(sa.Boolean, default=False)
    comments = sa.Column(sa.String, nullable=True)
    approval_status = sa.Column(sa.String,default="pending")  # Default status can be "pending", "approved", "rejected"
    is_admin = sa.Column(sa.Boolean,default=False)
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now, onupdate=utc_now)

    vsla_groups = relationship("Vsla", back_populates="psp", cascade="all, delete-orphan")
    password_data = relationship("PspPassword", uselist=False, back_populates="psp", cascade="all, delete")
    password_resets = relationship("PspPasswordReset", uselist=False, back_populates="psp", cascade="all, delete")