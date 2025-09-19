import sqlalchemy as sa
from datetime import datetime
from app.db.base import Base

class Member(Base):
    __tablename__ = "member"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    group_name = sa.Column(sa.String, nullable=False)
    membership_number = sa.Column(sa.String, nullable=False)
    country = sa.Column(sa.String)
    province = sa.Column(sa.String)
    district = sa.Column(sa.String)
    ward = sa.Column(sa.String)
    member_name = sa.Column(sa.String, nullable=False)
    id_number = sa.Column(sa.String,nullable=False)
    phone_number = sa.Column(sa.String)
    email = sa.Column(sa.String)
    office_position = sa.Column(sa.String)

    created_at = sa.Column(sa.DateTime(), default=datetime.now)
    updated_at = sa.Column(sa.DateTime(), default=datetime.now, onupdate=datetime.now)