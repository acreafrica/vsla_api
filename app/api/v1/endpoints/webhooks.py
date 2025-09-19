from ast import Str
from typing import List
import json
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import PlainTextResponse
#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, session

from app.crud import smsinbound as crud
from app.api.deps.db import get_db_session
from app.models import smsinbound as smsinboundmodel
from app.schemas import smsinbound as smsinboundschema



router = APIRouter()
#app = FastAPI()

@router.get("", response_class=PlainTextResponse,tags=['webhooks'])
def verify_url(request:Request,db: AsyncSession = Depends(get_db_session)):
    params = request.query_params
    print(params)
    print(params['hub.challenge'])
    valuesr=params['hub.challenge']
    return valuesr
@router.post("", tags=['webhooks'],status_code=200)
async def inbound_sms(*,request: Request, db: AsyncSession = Depends(get_db_session)):
    rbody=await request.body()
    json_object = json.loads(rbody)
    '''  Expected body object
    {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "8856996819413533",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505553333",
                            "phone_number_id": "27681414235104944"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Kerry Fisher"
                                },
                                "wa_id": "16315551234"
                            }
                        ],
                        "messages": [
                            {
                                "from": "16315551234",
                                "id": "wamid.ABGGFlCGg0cvAgo-sJQh43L5Pe4W",
                                "timestamp": "1603059201",
                                "text": {
                                    "body": "Hello this is an answer"
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}
    '''
    try:
        sms_id=json_object['entry'][0]['changes'][0]['value']['messages'][0]['id']
        print("this is sms id",sms_id)
        type=json_object['entry'][0]['changes'][0]['value']['messages'][0]['type']
        
        list_reply_id=""
        reply_tittle=""
        reply_description=""
        newinbound=await crud.get_sms_by_id(db,sms_id)
        if newinbound is None:
            Request_id=json_object['entry'][0]['id']
            display_phone=json_object['entry'][0]['changes'][0]['value']['metadata']['display_phone_number']
            phone_no_id=json_object['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
            contact_name=json_object['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            contact_wa_id=json_object['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            if type=="interactive":
                list_reply_id=text_body=json_object['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['id']
                reply_tittle=text_body=json_object['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['title']
                reply_description=text_body=json_object['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['description']
    # schema={'Request_id':Request_id,'display_phone':display_phone,'phone_no_id':phone_no_id,'contact_name':contact_name,'contact_wa_id':contact_wa_id,'sms_id':sms_id,'type':type,'text_body':text_body,'replied':False}
            if type=="text":
                text_body=json_object['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            smsinbound=smsinboundschema.smsinboundCreate(Request_id=Request_id,display_phone=display_phone,phone_no_id=phone_no_id,contact_name=contact_name,contact_wa_id=contact_wa_id,sms_id=sms_id,type=type,text_body=text_body,list_reply_id=list_reply_id,reply_tittle=reply_tittle,reply_description=reply_description)
            print("schema",smsinbound)
            smsinboundmodel=await crud.create_inbound(db,smsinbound)
    except Exception as e:
        print("error occured",e)           
    #print('body object',rbody)
    return  {"received_request_body": rbody}
    
@router.get("/smsinbounds/", tags=['inbounds'])
async def read_inbounds(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    inbounds =await crud.get_inbounds(db, skip=skip, limit=limit)
    return inbounds

@router.get("/readyinbounds/", tags=['ready inbounds'])
async def ready_inbounds(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    inbounds =await crud.get_ready_inbounds(db, limit=limit)
    return inbounds

# @router.get("/users/{user_id}", response_model=userschema.User, tags=['users'])
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
