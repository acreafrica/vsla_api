import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
class PspPassword(Base):
    __tablename__ = "psp_passwords"

    id = sa.Column(sa.Integer, primary_key=True)
    psp_id = sa.Column(sa.Integer, sa.ForeignKey("pspmodel.id"), nullable=False, unique=True)
    hashed_password = sa.Column(sa.String, nullable=False)

    psp = relationship("PspModel", back_populates="password_data")