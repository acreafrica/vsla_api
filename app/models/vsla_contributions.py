#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
def utc_now():
    return datetime.now(timezone.utc)

class Vsla_contributions(Base):
    __tablename__ = "vsla_contributions"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    vsla_id = sa.Column(sa.Integer, sa.ForeignKey("vsla.id"))
    month = sa.Column(sa.String)
    year = sa.Column(sa.String)
    amount = sa.Column(sa.Float)
    created_at = sa.Column(sa.DateTime(), default=utc_now)
    Updated_at = sa.Column(sa.DateTime(), default=utc_now,onupdate=utc_now)

    # ✅ Many-to-One: Vsla_members → Vsla
    #vsla_contributions = relationship("Vsla", back_populates="vslacontributions")
    vsla = relationship("Vsla", back_populates="contributions")