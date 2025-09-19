from typing import List, Optional
from datetime import datetime, date
#from pydantic import BaseModel
from app.schemas.base import BaseSchema
class ClaimBase(BaseSchema):
    member_id: int
    type_of_claim: int
    status: Optional[str] = "draft"  # draft, vetting, approval, paid, rejected
    class Config:
        arbitrary_types_allowed = True

class claimCreate(ClaimBase):
    pass

class claims(claimCreate):
    id: int
    created_at: datetime
    updated_at: datetime 
    class Config:
        orm_mode = True
class ClaimDocumentBase(BaseSchema):
    claim_id: int
    doc_type: str   # medical, invoice, burial_cert, etc.
    file_url: str
    class Config:
        arbitrary_types_allowed = True
class ClaimDocumentCreate(ClaimDocumentBase):
    pass
class ClaimDocument(ClaimDocumentBase):
    id: int
    created_at: datetime
    uploaded_at: datetime
    class Config:
        orm_mode = True
class ClaimReviewBase(BaseSchema):
    claim_id: int
    reviewer_id: int
    role: str       # leader, treasurer, sec, psp, admin
    comments: Optional[str] = None
    status: Optional[str] = "pending"     # pending, approved, rejected
    class Config:
        arbitrary_types_allowed = True
class ClaimReviewCreate(ClaimReviewBase):
    pass
class ClaimReview(ClaimReviewBase):
    id: int
    reviewed_at: datetime
    created_at: datetime
    class Config:
        orm_mode = True

class ClaimApprovalBase(BaseSchema):
    claim_id: int
    
    approver_id: int
    status: str  # approved, rejected
    comments: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
class ClaimApprovalCreate(ClaimApprovalBase):
    pass
class ClaimApproval(ClaimApprovalBase):
    id: int
    approved_at: datetime
    created_at: datetime
    class Config:
        orm_mode = True

class ClaimStatusSummary(BaseSchema):
    status: str
    total_claims: int

class VslaClaimSummary(BaseSchema):
    total_members: int
    total_claims: int
    claims_by_status: List[ClaimStatusSummary]