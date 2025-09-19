from ast import Str
from typing import List
import json
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import beneficiary as beneficiary_crud,vsla as vsla_crud
from app.models import beneficiary as BeneficiaryModel
from app.api.deps.dependencies import get_current_psp 
from app.schemas import beneficiary as beneficiaryschema
from app.api.deps.db import get_db_session
import pandas as pd
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_

router = APIRouter()
#app = FastAPI()

@router.post("/beneficiary/", response_model=beneficiaryschema.Beneficiary, tags=['beneficiary'])
async def create_benefiary(beneficiary: beneficiaryschema.BeneficiaryCreate, db: AsyncSession = Depends(get_db_session)):
    vsla=await vsla_crud.get_vsla_member_byid(db, vsla_id=beneficiary.vsla_member_id)
    if not vsla:
        raise HTTPException(status_code=400, detail="The specified vsla member does not exist.")
    beneficiary_exists = await beneficiary_crud.get_beneficiary_by_phone(phone=beneficiary.phone_number,db=db)
    if beneficiary_exists:
        raise HTTPException(status_code=400, detail="The beneficiary with this phone number already exists.")
    db_beneficiary = await beneficiary_crud.create_beneficiary(db, beneficiary=beneficiary,commit=True)
    
    return db_beneficiary

@router.get("/beneficiary/", response_model=List[beneficiaryschema.Beneficiary],tags=['beneficiary'])
async def list_beneficiaries(member_id:int,db: AsyncSession = Depends(get_db_session)):
    beneficiaries = await beneficiary_crud.get_beneficiary_by_principal(main_member_id=member_id,db=db)
    return beneficiaries
@router.get("/vsla_with_farmers")
async def list_farmers(db: AsyncSession = Depends(get_db_session)):
    farmers = await beneficiary_crud.get_farmers_with_beneficiaries(db)
    return farmers
