#from sqlalchemy import *
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class claims(Base):
    __tablename__ = "claims"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    member_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"))
    #type_of_claim = sa.Column(sa.String, nullable=False)
    type_of_claim = sa.Column(sa.Integer, sa.ForeignKey("product.id"))
    status = sa.Column(sa.String, default="draft")  # draft, vetting, approval, paid, rejected
    created_at = sa.Column(sa.DateTime, default=utc_now)
    updated_at = sa.Column(sa.DateTime, default=utc_now, onupdate=utc_now)
    
    # Relationship to Vsla_members
    member = relationship("Vsla_members", back_populates="claims")
    producttype = relationship("Product", back_populates="claims")
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan") 
    approvals = relationship("ClaimApproval", back_populates="claim", cascade="all, delete-orphan")
    reviews = relationship("ClaimReview", back_populates="claim", cascade="all, delete-orphan") 

class ClaimDocument(Base):
    __tablename__ = "claim_documents"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    claim_id = sa.Column(sa.Integer, sa.ForeignKey("claims.id"))
    doc_type = sa.Column(sa.String)   # medical, invoice, burial_cert, etc.
    file_url = sa.Column(sa.String)
    uploaded_at = sa.Column(sa.DateTime, default=utc_now)
    claim = relationship("claims", back_populates="documents")
    
class ClaimReview(Base):
    __tablename__ = "claim_reviews"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    claim_id = sa.Column(sa.Integer, sa.ForeignKey("claims.id"))
    reviewer_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"))
    role = sa.Column(sa.String)       # leader, treasurer, sec, psp, admin
    comments = sa.Column(sa.Text)
    status = sa.Column(sa.String)     # pending, approved, rejected
    reviewed_at = sa.Column(sa.DateTime, default=utc_now)
    claim = relationship("claims", back_populates="reviews")
    reviewer = relationship("Vsla_members")

class ClaimApproval(Base): # BY TREASURER, SECRETARY
    __tablename__ = "claim_approvals"   
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    claim_id = sa.Column(sa.Integer, sa.ForeignKey("claims.id"))
    approver_id = sa.Column(sa.Integer, sa.ForeignKey("vsla_members.id"))
    approved_at = sa.Column(sa.DateTime, default=utc_now)
    comments = sa.Column(sa.String, nullable=True)
    status = sa.Column(sa.String)  # approved, rejected
    claim = relationship("claims", back_populates="approvals")
    reviewer = relationship("Vsla_members")
   # review = relationship("ClaimReview", back_populates="approval")
    