from sqlalchemy import select, update,desc,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import claims as ClaimModel,product as productmodel #models
from app.schemas import product as productschema 
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
#from . import models, schemas


async def get_product(product_id: int,db: AsyncSession, skip: int = 0, limit: int = 100):#-> List[VslaModel.Vsla]:
    result = await db.execute(
            select(productmodel.Product)
            .filter(productmodel.Product.id == product_id)    
        )
    await db.commit()
    return result.scalars().one_or_none()

async def get_all_products(db: AsyncSession)   :
    result = await db.execute(
        select(productmodel.Product)
        .order_by(productmodel.Product.id)
    )
    return result.scalars().all()

async def create_product(db: AsyncSession, product: productschema.ProductCreate,commit=True):
    obj_in_data = jsonable_encoder(product, exclude_unset=True)
    db_product = productmodel.Product(**obj_in_data)
    db.add(db_product)
    if commit:
        await db.commit()
    else:
        await db.flush()
 
    return db_product





