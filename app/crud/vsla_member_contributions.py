from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import vsla_member_contributions as membercontributionsModel,vsla_members as vslamembersmodel,vsla as vslaModel #models
from app.schemas import vsla_member_contributions as VslaMembercontributionschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


async def get_member_contribution(db: AsyncSession, vsla_id: int):
    result = await db.execute(membercontributionsModel.Vsla_member_contributions).filter(membercontributionsModel.Vsla_member_contributions.vsla_member_id== vsla_id).first()
    return result.scalars().all()

async def get_contribution_per_member(db: AsyncSession,member_id:int)-> List[membercontributionsModel.Vsla_member_contributions]:
    result = await db.execute(
            select(membercontributionsModel.Vsla_member_contributions)
            .filter(membercontributionsModel.Vsla_member_contributions.vsla_member_id==member_id)
             )
    return result.scalars().all()

async def get_contribution_per_vsla(db: AsyncSession,vsla_id:int):#-> List[VslaMembercontributionschema.Vsla_members_contributions]:
    # stmt = (
    #     select(membercontributionsModel.Vsla_member_contributions)
    #     .join(
    #         vslamembersmodel.Vsla_members,
    #         membercontributionsModel.Vsla_member_contributions.vsla_member_id == vslamembersmodel.Vsla_members.id
    #     )
    #     .where(vslamembersmodel.Vsla_members.vsla_id == vsla_id)
    #     .order_by(
    #         membercontributionsModel.Vsla_member_contributions.year,
    #         membercontributionsModel.Vsla_member_contributions.month
    #     )
    #     )
    # result = await db.execute(stmt)
    # return result.mappings().all()
    stmt = (
        select(
            membercontributionsModel.Vsla_member_contributions.id,
            vslamembersmodel.Vsla_members.member_name,
            membercontributionsModel.Vsla_member_contributions.month,
            membercontributionsModel.Vsla_member_contributions.year,
            membercontributionsModel.Vsla_member_contributions.amount,
            vslaModel.Vsla.vsla_group_name.label("vsla_name"),
            membercontributionsModel.Vsla_member_contributions.created_at,
            membercontributionsModel.Vsla_member_contributions.Updated_at
        )
        .join(
            vslamembersmodel.Vsla_members,
            membercontributionsModel.Vsla_member_contributions.vsla_member_id
            == vslamembersmodel.Vsla_members.id
        )
        .join(
            vslaModel.Vsla,
            vslamembersmodel.Vsla_members.vsla_id == vslaModel.Vsla.id
        )
        .where(vslamembersmodel.Vsla_members.vsla_id == vsla_id)
        .order_by(
            membercontributionsModel.Vsla_member_contributions.year,
            membercontributionsModel.Vsla_member_contributions.month
        )
    )
    result = await db.execute(stmt)
    return result.mappings().all()

   
   




