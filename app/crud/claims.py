from sqlalchemy import select, update,desc,func
from sqlalchemy.orm import Session,aliased,joinedload,selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import claims as ClaimModel,vsla_members as vslamembers,ClaimDocument,ClaimReview,ClaimApproval #models
from app.schemas import claim as claimschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


async def get_vsla_members_vsla(vsla_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(vslamembers.Vsla_members)
            .filter(vslamembers.Vsla_members.vsla_id == vsla_id)    
            .order_by(vslamembers.Vsla_members.id)
            .offset(skip)
            .limit(limit)
        )
    await db.commit()
    return result.scalars().all()

async def get_claims_by_id(db: AsyncSession, claim_id: int):
    result = await db.execute(
            select(ClaimModel)
            .filter(ClaimModel.id == claim_id)    
        )
    await db.commit()
    return result.scalars().one_or_none()

async def create_claims(db: AsyncSession, claim: claimschema.claimCreate,commit=True):
    obj_in_data = jsonable_encoder(claim, exclude_unset=True)
    db_claim = ClaimModel(**obj_in_data)
    db.add(db_claim)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_claim

async def update_claims(db: AsyncSession, db_claim: claimschema.claims, updates: Dict[str, Any], commit=True):
    for key, value in updates.items():
        setattr(db_claim, key, value)
    db.add(db_claim)
    if commit:
        await db.commit()
    else:
        await db.flush()
    await db.refresh(db_claim)
    return db_claim
async def get_claim_per_vsla_member(db: AsyncSession,vsla_member_id: int, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(ClaimModel)
            .join(vslamembers.Vsla_members, ClaimModel.member_id == vslamembers.Vsla_members.id)
            .filter(vslamembers.Vsla_members.id == vsla_member_id)    
            .order_by(ClaimModel.id)
            .offset(skip)
            .limit(limit)
        )
    await db.commit()
    return result.scalars().all()
async def get_claim_documents(claim_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(ClaimModel.ClaimDocument)
            .filter(ClaimModel.ClaimDocument.claim_id == claim_id)    
            .order_by(ClaimModel.ClaimDocument.id)
            .offset(skip)
            .limit(limit)
        )
    await db.commit()
    return result.scalars().all()
async def create_claim_document(db: Session, document: claimschema.ClaimDocumentCreate,commit=True):
    obj_in_data = jsonable_encoder(document, exclude_unset=True)
    db_document = ClaimDocument(**obj_in_data)
    db.add(db_document)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_document
async def get_claim_reviews(claim_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(  
            select(ClaimReview)
            .filter(ClaimReview.claim_id == claim_id)    
            .order_by(ClaimReview.id)
            .offset(skip)
            .limit(limit)
        )   
    await db.commit()
    return result.scalars().all()       
async def create_claim_review(db: Session, review: claimschema.ClaimReviewCreate,commit=True):
    obj_in_data = jsonable_encoder(review, exclude_unset=True)
    db_review = ClaimReview(**obj_in_data)
    db.add(db_review)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_review
async def get_claim_approvals(claim_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(ClaimModel.ClaimApproval)
            .filter(ClaimModel.ClaimApproval.claim_id == claim_id)    
            .order_by(ClaimModel.ClaimApproval.id)
            .offset(skip)
            .limit(limit)
        )           
    await db.commit()
    return result.scalars().all()      
async def create_claim_approval(db: Session, approval: claimschema.ClaimApprovalCreate,commit=True):
    obj_in_data = jsonable_encoder(approval, exclude_unset=True)
    db_approval = ClaimApproval(**obj_in_data)
    db.add(db_approval)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_approval                                                            


async def get_claim_summary_by_vsla(db: AsyncSession, vsla_id: int):
    # stmt = (
    #     select(
    #         ClaimModel.status,
    #         func.count(ClaimModel.id).label("total_claims")
    #     )
    #     .join(vslamembers.Vsla_members, ClaimModel.member_id == vslamembers.Vsla_members.id)
    #     .where(vslamembers.Vsla_members.vsla_id == vsla_id)
    #     .group_by(ClaimModel.status)
    # )

    # result = await db.execute(stmt)
    # rows = result.all()

    # # Return as list of dicts
    # return [
    #     {"status": status, "total_claims": total_claims}
    #     for status, total_claims in rows
    # ]
    Members = vslamembers.Vsla_members

    # Subquery for total members
    total_members_subq = select(func.count(Members.id)).where(Members.vsla_id == vsla_id).scalar_subquery()

    # Subquery for total claims
    total_claims_subq = (
        select(func.count(ClaimModel.id))
        .join(Members, ClaimModel.member_id == Members.id)
        .where(Members.vsla_id == vsla_id)
        .scalar_subquery()
    )

    # Main query: claims per status + include total_members & total_claims as constants
    stmt = (
        select(
            ClaimModel.status,
            func.count(ClaimModel.id).label("claims_per_status"),
            total_members_subq.label("total_members"),
            total_claims_subq.label("total_claims")
        )
        .join(Members, ClaimModel.member_id == Members.id)
        .where(Members.vsla_id == vsla_id)
        .group_by(ClaimModel.status)
    )

    result = await db.execute(stmt)
    rows = result.all()

    claims_by_status = [
        {"status": status, "total_claims": claims_per_status}
        for status, claims_per_status, _, _ in rows
    ]

    total_members = rows[0][2] if rows else 0
    total_claims = rows[0][3] if rows else 0

    return {
        "total_members": total_members,
        "total_claims": total_claims,
        "claims_by_status": claims_by_status
    }
async def get_claims(db: AsyncSession, skip: int = 0, limit: int = 100):
    # result = await db.execute(
    #         select(ClaimModel)
    #         .order_by(ClaimModel.id)
    #         .offset(skip)
    #         .limit(limit)
    #     )
    # await db.commit()
    # return result.scalars().all()
    result = await db.execute(
        select(ClaimModel)
        .options(joinedload(ClaimModel.member))   # 👈 eager load the member
         .options(joinedload(ClaimModel.producttype)) 
        .order_by(ClaimModel.id)
        .offset(skip)
        .limit(limit)
    )
    #return result.scalars().all()
    claim_list = result.scalars().all()

    # flatten to include only member_name
    return [
    {
        "id": c.id,
        "type_of_claim": c.type_of_claim,
        "status": c.status,
        "created_at": c.created_at,
        "member_name": c.member.member_name if c.member else None,
        "product_name": c.producttype.name if c.producttype else None  
    }
    for c in claim_list
]

async def get_claim_details(db: AsyncSession, claim_id: int):
    result = await db.execute(
        select(ClaimModel)
        .options(
            selectinload(ClaimModel.member),
            selectinload(ClaimModel.producttype),
            selectinload(ClaimModel.documents),
            selectinload(ClaimModel.reviews).selectinload(ClaimReview.reviewer),
            selectinload(ClaimModel.approvals).selectinload(ClaimApproval.reviewer)
        )
        .where(ClaimModel.id == claim_id)
    )

    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return {
        "id": claim.id,
        "status": claim.status,
        "created_at": claim.created_at,
        "member_name": claim.member.member_name if claim.member else None,
        "product_name": claim.producttype.name if claim.producttype else None,

        # documents
        "documents": [
            {"doc_type": d.doc_type, "file_url": d.file_url}
            for d in claim.documents
        ],

        # reviews
        "reviews": [
            {
                "reviewer": r.reviewer.member_name if r.reviewer else None,
                "role": r.role,
                "status": r.status,
                "comments": r.comments,
                "reviewed_at": r.reviewed_at
            }
            for r in claim.reviews
        ],

        # approvals
        "approvals": [
            {
                "approver": a.reviewer.member_name if a.reviewer else None,
                "status": a.status,
                "comments": a.comments,
                "approved_at": a.approved_at
            }
            for a in claim.approvals
        ],
    }