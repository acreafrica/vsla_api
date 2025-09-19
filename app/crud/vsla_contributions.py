from sqlalchemy import select, update,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import vsla_contributions as vslacontributionsmodel,vsla as vsla_model #models
from app.schemas import vsla_member_contributions as VslaMembercontributionschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas




async def get_contribution_per_vsla(db: AsyncSession,vsla_id:int):
    # result = await db.execute(
    #         select(vslacontributionsmodel.Vsla_contributions)
    #         .filter(vslacontributionsmodel.Vsla_contributions.vsla_id==vsla_id)
    #          )
    # return result.scalars().all()
    result = await db.execute(
        select(
            vslacontributionsmodel.Vsla_contributions.id,
            vsla_model.Vsla.vsla_group_name.label("vsla_name"),
            vslacontributionsmodel.Vsla_contributions.month,
            vslacontributionsmodel.Vsla_contributions.year,
            vslacontributionsmodel.Vsla_contributions.amount,
            vslacontributionsmodel.Vsla_contributions.created_at,
            vslacontributionsmodel.Vsla_contributions.Updated_at
        ).join(
            vsla_model.Vsla,
            vsla_model.Vsla.id == vslacontributionsmodel.Vsla_contributions.vsla_id
        ).filter(
            vslacontributionsmodel.Vsla_contributions.vsla_id == vsla_id
        )
    )
    # ✅ use .mappings() so FastAPI can serialize the results
    return result.mappings().all()

async def get_monthly_contributions(psp_id: int, db: AsyncSession):
    stmt = (
        select(
            vslacontributionsmodel.Vsla_contributions.year,
            vslacontributionsmodel.Vsla_contributions.month,
            func.sum(vslacontributionsmodel.Vsla_contributions.amount).label("total_contributions")
        )
        .join(vsla_model.Vsla, vslacontributionsmodel.Vsla_contributions.vsla_id == vsla_model.Vsla.id)
        .filter(vsla_model.Vsla.psp_id == psp_id)
        .group_by(vslacontributionsmodel.Vsla_contributions.year, vslacontributionsmodel.Vsla_contributions.month)
        .order_by(vslacontributionsmodel.Vsla_contributions.year, vslacontributionsmodel.Vsla_contributions.month)
    )
    result = await db.execute(stmt)
    return result.all()  # returns list of tuples: (year, month, total_contributions)


   
   




