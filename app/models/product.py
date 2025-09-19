#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class Product(Base):
    __tablename__ = "product"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    sum_insured = sa.Column(sa.Integer)
    comments = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now,onupdate=utc_now)
    require_medical_report = sa.Column(sa.Boolean, default=False)
    require_invoice = sa.Column(sa.Boolean, default=False)
    require_burial_cert = sa.Column(sa.Boolean, default=False)
    require_discharge_letter = sa.Column(sa.Boolean, default=False)

    claims = relationship("claims", back_populates="producttype", cascade="all, delete-orphan")
