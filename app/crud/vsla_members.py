from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import vsla_members as VslaMembersModel #models
from app.schemas import vsla_members as VslaMembersschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


def get_vsla_member(db: Session, vsla_id: int):
    return db.query(VslaMembersModel.Vsla).filter(VslaMembersModel.Vsla.id == vsla_id).first()


async def get_vsla_by_id(db: AsyncSession, vsla_member_idnumber: str,vsla_id: int):
    vsla_member_idnumber = str(vsla_member_idnumber) 
    result = await db.execute(
            select(VslaMembersModel.Vsla_members)
            .filter(VslaMembersModel.Vsla_members.id_number==vsla_member_idnumber)
             )
    return result.scalars().one_or_none()
async def get_vsla_by_phone(db: AsyncSession, vsla_member_phone: str,vsla_id: int):
    vsla_member_phone = str(vsla_member_phone) 
    result = await db.execute(
            select(VslaMembersModel.Vsla_members)
            .filter(VslaMembersModel.Vsla_members.phone_number==vsla_member_phone)
             )
    return result.scalars().first()

async def get_vsla_members_per_vsla(db: AsyncSession, skip: int = 0, limit: int = 100)-> List[VslaMembersModel.Vsla_members]:
    result = await db.execute(
            select(VslaMembersModel.Vsla_members)
            .order_by(VslaMembersModel.Vsla_members.id)
            .offset(skip)
            .limit(limit)
        )
    await db.commit()
    return result.scalars().all()

async def get_all_vsla_members(db: AsyncSession, skip: int = 0, limit: int = 100)-> List[VslaMembersModel.Vsla_members]:
    result = await db.execute(
            select(VslaMembersModel.Vsla_members)
            .order_by(VslaMembersModel.Vsla_members.id)
            .offset(skip)
            .limit(limit)
        )
    return result.scalars().all()




async def create_vsla_members(db: Session, vsla_member: VslaMembersschema.Vsla_membersCreate,commit=True):
    obj_in_data = jsonable_encoder(vsla_member, exclude_unset=True)
    db_vsla_member = VslaMembersModel.Vsla_members(**obj_in_data)
    db.add(db_vsla_member)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_vsla_member

   
   




