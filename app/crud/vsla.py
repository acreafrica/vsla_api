from sqlalchemy import select, update,desc,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import vsla as VslaModel,vsla_members as vslamembers #models
from app.schemas import vsla as Vslaschema ,vsla_members as vsla_membersschema
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


def get_vsla(db: Session, vsla_id: int):
    return db.query(VslaModel.Vsla).filter(VslaModel.Vsla.id == vsla_id).first()

async def get_vsla_member_byid(db: Session, vsla_id: int):
    result = await db.execute(
            select(vslamembers.Vsla_members)
            .filter(vslamembers.Vsla_members.id==vsla_id)#, VslaModel.Vsla.psp_id==psp_id
             )
    await db.commit()
    return result.scalars().one_or_none()

async def get_vsla_by_name(db: AsyncSession, vsla_name: str,psp_id: int):
    result = await db.execute(
            select(VslaModel.Vsla)
            .filter(VslaModel.Vsla.vsla_group_name==vsla_name)#, VslaModel.Vsla.psp_id==psp_id
             )
    await db.commit()
    return result.scalars().one_or_none()
async def get_vsla_by_id(db: AsyncSession, vsla_id: int):
    result = await db.execute(
            select(VslaModel.Vsla)
            .filter(VslaModel.Vsla.id==vsla_id)#, VslaModel.Vsla.psp_id==psp_id
             )
    await db.commit()
    return result.scalars().one_or_none()

async def get_vsla_per_psp(psp_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
   
    result = await db.execute(
        select(
            VslaModel.Vsla.id,
            VslaModel.Vsla.vsla_group_name,
            func.count(vslamembers.Vsla_members.id).label("member_count")
        )
        .join(
            vslamembers.Vsla_members,
            vslamembers.Vsla_members.vsla_id == VslaModel.Vsla.id,
            isouter=True
        )
        .filter(VslaModel.Vsla.psp_id == psp_id)
        .group_by(VslaModel.Vsla.id, VslaModel.Vsla.vsla_group_name)
        .order_by(desc(VslaModel.Vsla.id))
        .offset(skip)
        .limit(limit)
    )

    rows = result.all()  # ✅ tu keep .all() kwa tuples

    return [
        {"id": id_, "vsla_group_name": name, "member_count": count}
        for id_, name, count in rows
    ]
   

async def get_all_vsla(db: AsyncSession, skip: int = 0, limit: int = 100)-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(VslaModel.Vsla)
            .order_by(VslaModel.Vsla.id)
            .offset(skip)
            .limit(limit)
        )
    await db.commit()
    return result.all()

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


async def get_total_members_vsla(vsla_id: int,db: AsyncSession):#-> List[VslaModel.Vsla]:
    result = await db.execute(
        select(func.count())
        .select_from(vslamembers.Vsla_members)
        .filter(vslamembers.Vsla_members.vsla_id == vsla_id)
    )
    total_count = result.scalar()
    return total_count


async def create_vsla(db: Session, vsla: Vslaschema.VslaCreate,commit=True):
    obj_in_data = jsonable_encoder(vsla, exclude_unset=True)
    db_vsla = VslaModel.Vsla(**obj_in_data)
    db.add(db_vsla)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_vsla

async def update_vsla_member_in_db(
    db: AsyncSession,
    member_id: int,
    member_update: vsla_membersschema.VslaMemberUpdate
):
    # Find member
    result = await db.execute(
        select(vslamembers.Vsla_members).where(vslamembers.Vsla_members.id == member_id)
    )
    member = result.scalars().first()

    if not member:
        raise HTTPException(status_code=404, detail="VSLA member not found")

    # Apply only provided fields
    update_data = member_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)

    await db.commit()
    await db.refresh(member)
    return member   
   




