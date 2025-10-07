from ast import Str
from typing import List
import json
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import vsla as crud,products as product_crud
from app.models import vsla as vslamodel,vslacsvmodel,vsla_members as vsla_membersModel,pspmodel as PspModel,vsla_member_contributions as VslaContribution
from app.api.deps.dependencies import get_current_psp 
from app.schemas import product as productschema
from app.api.deps.db import get_db_session
import pandas as pd
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_

router = APIRouter()
#app = FastAPI()
EXPECTED_COLUMNS = [
    "Group Name", "Membership Number", "Country", "Province", "District", "Ward",
    "Member Name", "ID Number", "Phone Number", "Email", "Office Position"
]
CONTRIBUTIONS_COLUMNS = ["member_phone", "month", "year", "amount"]
@router.post("/products/", response_model=productschema.Product, tags=['products'])
async def create_or_update_product(product: productschema.ProductCreateOrUpdate, db: AsyncSession = Depends(get_db_session)):
    db_product = await product_crud.create_or_update_product(db, product=product,commit=True)
    return db_product

@router.post("/products/delete", tags=['products'])
async def delete_product(product: productschema.ProductDelete, db: AsyncSession = Depends(get_db_session)):
    db_product = await product_crud.delete_product(db, product=product,commit=True)
    return db_product

@router.get("/products/", response_model=List[productschema.Product],tags=['products'])
async def list_products(db: AsyncSession = Depends(get_db_session)):
    products = await product_crud.get_all_products(db)
    return products
    
