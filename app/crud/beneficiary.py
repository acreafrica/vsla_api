from sqlalchemy import select, update,desc,func
from sqlalchemy.orm import Session,selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import beneficiary as beneficiaryModel,vsla_members as Vsla_members
from app.schemas import beneficiary as beneficiaryschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


async def get_beneficiary(beneficiary_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(beneficiaryModel.Beneficiary)
            .filter(beneficiaryModel.Beneficiary.id == beneficiary_id)    
        )
    await db.commit()
    return result.scalars().one_or_none()
async def get_beneficiary_by_phone(phone: str,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(beneficiaryModel.Beneficiary)
            .filter(beneficiaryModel.Beneficiary.phone_number == phone)    
        )
    await db.commit()
    return result.scalars().one_or_none()
async def get_beneficiary_by_principal(main_member_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(beneficiaryModel.Beneficiary)
            .filter(beneficiaryModel.Beneficiary.vsla_member_id == main_member_id)    
        )
    await db.commit()
    return result.scalars().all()
async def get_all_beneficiaries(db: AsyncSession)   :
    result = await db.execute(
        select(beneficiaryModel.Beneficiary)
        .order_by(beneficiaryModel.Beneficiary.id)
    )
    return result.scalars().all()

async def create_beneficiary(db: AsyncSession, beneficiary: beneficiaryschema.BeneficiaryCreate,commit=True):
    obj_in_data = jsonable_encoder(beneficiary, exclude_unset=True)
    db_beneficiary = beneficiaryModel.Beneficiary(**obj_in_data)
    db.add(db_beneficiary)
    if commit:
        await db.commit()
    else:
        await db.flush()
    await db.refresh(db_beneficiary)
    return db_beneficiary
async def get_farmers_with_beneficiaries(db: AsyncSession):
    result = await db.execute(
        select(Vsla_members.Vsla_members)
        .options(selectinload(Vsla_members.Vsla_members.beneficiaries))
    )
    farmers = result.scalars().all()
    return farmers




