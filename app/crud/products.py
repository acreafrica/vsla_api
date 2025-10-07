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


async def create_or_update_product(
    db: AsyncSession, product: productschema.ProductCreateOrUpdate, commit: bool = True
):
    
    try:
        # If updating (id provided)
        if product.id is not None:
            # here we update the items of this product 
            result = await db.execute(
                select(productmodel.Product).filter(productmodel.Product.id == product.id)
            )
            db_product = result.scalar_one_or_none()
            if db_product:
                # update fields
                for key, value in vars(product).items():
                    setattr(db_product, key, value)
                if commit:
                    await db.commit()
                    await db.refresh(db_product)
                else:
                    await db.flush()
                return db_product
            return None
        
        # Otherwise create new
        db_product = productmodel.Product(**vars(product))
        db.add(db_product)
        if commit:
            await db.commit()
            await db.refresh(db_product)
        else:
            await db.flush()

        return db_product
    except Exception as e:
        print(e)
        raise(e)



async def delete_product(
    db: AsyncSession, product: productschema.ProductDelete, commit: bool = True
):
    try:
        if product.id is not None:
            result = await db.execute(
                select(productmodel.Product).filter(productmodel.Product.id == product.id)
            )
            db_product = result.scalar_one_or_none()
            if db_product:
                await db.delete(db_product)
                if commit:
                    await db.commit()
                else:
                    await db.flush()
                return {"deleted_product_id": product.id}
            return None
    except Exception as e:
        print(e)
        raise(e)





