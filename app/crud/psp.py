from http.client import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import pspmodel as pspmodel #models
from app.schemas import psp as pspschema #models
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


def get_psp(db: Session, psp_id: int):
    return db.query(pspmodel.User).filter(pspmodel.PspModel.id == psp_id).first()

async def get_psp_by_id(db: AsyncSession, id: int):
    result = await db.execute(
            select(pspmodel.PspModel)
            .filter(pspmodel.PspModel.id==id)
             )
    await db.commit()
    return result.scalars().one_or_none()
async def get_psp_by_email(db: AsyncSession, email: str):
    result = await db.execute(
            select(pspmodel.PspModel)
            .filter(pspmodel.PspModel.email==email)
             )
    await db.commit()
    return result.scalars().one_or_none()
async def get_psp_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(
            select(pspmodel.PspModel)
            .filter(pspmodel.PspModel.phone_number==phone)
             )
    await db.commit()
    return result.scalars().first()

async def get_psp(db: AsyncSession,status:int=None, skip: int = 0, limit: int = 100)-> List[pspmodel.PspModel]:
    # result = await db.execute(
    #         select(pspmodel.PspModel)
    #         .order_by(pspmodel.PspModel.id)
    #         .offset(skip)
    #         .limit(limit)
    #     )
    # await db.commit()
    # return result.scalars().all()
     query = select(pspmodel.PspModel).order_by(pspmodel.PspModel.id)

    # map numeric status to approval_status string
     if status is not None:
        status_map = {
            0: "pending",
            1: "approved",
            2: "rejected"
        }
        if status in status_map:
            query = query.where(pspmodel.PspModel.approval_status == status_map[status])

     query = query.offset(skip).limit(limit)

     result = await db.execute(query)
     return result.scalars().all()

async def approve_psp_by_id(db: AsyncSession, id: int,status:int,is_admin:int=0):
    status_map = {
            0: "pending",
            1: "approved",
            2: "rejected"
        }
    # if status not in status_map:
    #     return None  # or raise an exception

    # stmt = (
    #     update(pspmodel.PspModel)
    #     .where(pspmodel.PspModel.id == id)
    #     .values(approval_status=status_map[status])
    #     .execution_options(synchronize_session="fetch")
    # )
    # result = await db.execute(stmt)
    # await db.commit()
    # if result.rowcount == 0:
    #     return None
    # return await get_psp_by_id(db, id=id)
    if status not in status_map:
        #return None  # or 
        raise HTTPException(status_code=400, detail="Invalid status")

    if is_admin not in [0, 1]:
        #return None  # or 
        raise HTTPException(status_code=400, detail="Invalid admin_status")

    # stmt = (
    #     update(pspmodel.PspModel)
    #     .where(pspmodel.PspModel.id == id)
    #     .values(
    #         approval_status=status_map[status],
    #         is_admin=is_admin  # 🔥 added this
    #     )
    #     .execution_options(synchronize_session="fetch")
        
    # )
    stmt = (
        update(pspmodel.PspModel.__table__)   # 👈 use __table__ to avoid ORM OUTPUT
        .where(pspmodel.PspModel.id == id)
        .values(
            approval_status=status_map[status],
            is_admin=is_admin
           # Updated_at=datetime.now(timezone.utc)
        )
    )

    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        return None

    return await get_psp_by_id(db, id=id)
async def create_psp(db: Session, psp: pspschema.pspCreate,commit=True):
    obj_in_data = jsonable_encoder(psp, exclude_unset=True)
    db_smsinbound = pspmodel.PspModel(**obj_in_data)
    db.add(db_smsinbound)
    if commit:
        await db.commit()
    else:
        await db.flush()
    

    return db_smsinbound

   
   




