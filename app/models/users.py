from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Verifyurl(Base):
    __tablename__ = "verifyurl"

    id = Column(Integer, primary_key=True, index=True)
    hub_mode = Column(String)
    hub_challenge = Column(String)
    hub_verify_token = Column(String)



class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
  