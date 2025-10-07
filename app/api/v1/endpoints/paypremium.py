from ast import Str
from typing import List
import json
import requests
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import vsla as crud,products as product_crud
from app.models import vsla as vslamodel,vslacsvmodel,vsla_members as vsla_membersModel,pspmodel as PspModel,vsla_member_contributions as VslaContribution
from app.api.deps.dependencies import get_current_psp, get_current_user 
from app.schemas import product as productschema
from app.api.deps.db import get_db_session
import pandas as pd
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_
from datetime import datetime

router = APIRouter()
#app = FastAPI()

@router.post("/premium_lipila/", tags=['premium'])
async def pay_lipila(phone_number:str,Amount:float ,RefNo:str='', db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    if current_user.usertype != "vsla_member":
         raise HTTPException(status_code=400, detail="Only vsla members/leaders can pay premium")
    vsla_id=current_user.vsla_id
    external_id = datetime.now().strftime("%m%d%H%M%S")
    url = "https://lipila-prod.hobbiton.app/transactions/mobile-money"

    headers = {
        "Authorization": "Bearer LPLSECK-aa247da5d2694612b320aac2907bd463",  # 🔑 Replace with your actual secret key
        "Content-Type": "application/json"
    }

    payload = {
        "currency": "ZMW",
        "amount": Amount,
        "accountNumber":phone_number,# current_user.vsa_id,  # Assuming vsla_id is the account number
        "fullName": "",
        "phoneNumber": phone_number,
        "email": "Apps@acreafrica.com",
        "externalId": f"{vsla_id}_{external_id}",#vsla_id+'_'+external_id,
        "narration": "Payment For premium"
    }

    try:
        # 🕒 Set timeout to 60 seconds
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print("✅ Status Code:", response.status_code)
        print("📄 Response Body:")
        print(response.text)

    except requests.exceptions.Timeout:
        print("⏳ Request timed out after 60 seconds.")
        raise HTTPException(status_code=504, detail="Request timed out after 60 seconds.")  
    except requests.exceptions.RequestException as e:
        print("❌ Request Error:", e)
        raise HTTPException(status_code=500, detail=f"Request Error: {e}")
    return {"status": "Payment request sent", "response": response.json()}
    

@router.get("/premium_cgrate/", tags=['premium'])
async def pay_cgrate(db: AsyncSession = Depends(get_db_session)):
    products = await product_crud.get_all_products(db)
    return products
    
