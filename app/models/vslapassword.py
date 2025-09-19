import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
class VslaPassword(Base):
    __tablename__ = "vsla_password"

    id = sa.Column(sa.Integer, primary_key=True)
    vsla_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"), nullable=False, unique=True)
    hashed_password = sa.Column(sa.String, nullable=False)

    vsla = relationship("Vsla_members", back_populates="password_data")

class VslaPasswordReset(Base):
    __tablename__ = "vsla_password_resets"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    vsla_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"))
    otp_code = sa.Column(sa.String, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=False)

    #vsla_reset = relationship("Vsla_members", backref="password_resets")
    vsla = relationship("Vsla_members", back_populates="password_resets")

class PspPasswordReset(Base):
    __tablename__ = "psp_password_resets"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    psp_id = sa.Column(sa.Integer, sa.ForeignKey("pspmodel.id"))
    otp_code = sa.Column(sa.String, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=False)

    #vsla_reset = relationship("Vsla_members", backref="password_resets")
    psp = relationship("PspModel", back_populates="password_resets")