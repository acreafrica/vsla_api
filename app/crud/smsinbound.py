from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import smsinbound as smsinboundmodel #models
from app.schemas import smsinbound as smsinboundschema #models
from sqlalchemy import select, update
from fastapi.encoders import jsonable_encoder
import http.client
import json
#from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(smsinboundmodel.User).filter(smsinboundmodel.User.id == user_id).first()

async def get_sms_by_id(db: AsyncSession, sms_id: str):
    result = await db.execute(
            select(smsinboundmodel.SmsInbound)
            .filter(smsinboundmodel.SmsInbound.sms_id==sms_id)
             )
    await db.commit()
    return result.scalars().one_or_none()
    
async def create_inbound(db: Session, smsinbound: smsinboundschema.smsinboundCreate,commit=True):

    obj_in_data = jsonable_encoder(smsinbound, exclude_unset=True)
    db_smsinbound = smsinboundmodel.SmsInbound(**obj_in_data)
    db.add(db_smsinbound)
    if commit:
        await db.commit()
    else:
        await db.flush()
    

    return db_smsinbound
    

async def get_inbounds(db: AsyncSession, skip: int = 0, limit: int = 100)-> List[smsinboundmodel.SmsInbound]:
        result = await db.execute(
            select(smsinboundmodel.SmsInbound)
            .offset(skip)
            .limit(limit)
        )
        await db.commit()
        return result.scalars().all()

async def get_ready_inbounds(db: AsyncSession, skip: int = 0, limit: int = 100)-> List[smsinboundmodel.SmsInbound]:
        result = await db.execute(
            select(smsinboundmodel.SmsInbound)
            .filter(smsinboundmodel.SmsInbound.replied==False)
            .offset(skip)
            .limit(limit)
        )
        await db.commit()
        return result.scalars().all()
async def get_all_waiting(db: AsyncSession, limit: int = 100):
    result = await db.execute(
            select(smsinboundmodel.SmsInbound).filter(smsinboundmodel.SmsInbound.replied==False).limit(limit)
        )
    await db.commit()
    return result.scalars().all()

async def sentsms(tokenstr:str,phone:str,message:str,prevsmsid:str):
    ''' sms body object
    {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "{{Recipient-Phone-Number}}",
    "context": {
        "message_id": "<MSGID_OF_PREV_MSG>"
    },
    "type": "text",
    "text": {
        "preview_url": false,
        "body": "<TEXT_MSG_CONTENT>"
    }
}'''
    print("reached sent sms",phone)
    bodyobj={
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": phone,
    "context": {
        "message_id": prevsmsid
    },
    "type": "text",
    "text": {
        "preview_url": False,
        "body": message
    }
    }
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload1 = json.dumps(bodyobj)
    payload = json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "{{phone}}",
    "context": {
        "message_id": "{{prevsmsid}}"
    },
    "type": "text",
    "text": {
        "preview_url": False,
        "body": "{{message}}"
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+tokenstr
    }
    print
    print(payload1,headers)
    conn.request("POST", "/v14.0/103570139153202/messages", payload1, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))#
    return payload 
async def sentsmsinteractive(tokenstr:str,phone:str,message:str,prevsmsid:str,db:AsyncSession):
    ''' sms body object
   {
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "254723369600",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": {
      "type": "text",
      "text": "Cross Gate Solutions"
    },
    "body": {
      "text": "Our Services"
    },
    "footer": {
      "text": "Check on us"
    },
    "action": {
      "button": "BUTTON_TEXT",
      "sections": [
        {
          "title": "Select Option",
          "rows": [
            {
              "id": "Bulk_sms",
              "title": "Bulk services",
              "description": "with custom sender id"
            },
            {
              "id": "USSD",
              "title": "USSD services",
              "description": "with dedicated or shared codes"
            },
             {
              "id": "short_code",
              "title": "premium codes",
              "description": "Pay for Nairobi water"
            },
             {
              "id": "M_PESA",
              "title": "M PESA",
              "description": "M pesa integrations"
            }
          ]
        }
      ]
    }
  }
}'''
    print("reached sent sms",phone)
    currentsms:smsinboundmodel.SmsInbound=await get_sms_by_id(db,prevsmsid)
    if currentsms is not None:
        if currentsms.list_reply_id=="Rates":
          smstext="We offer bulk at the following rates: \n 1-100k units at ksh 1.00 \n 100k-500k units at ksh 0.8 \n 500k-1m at ksh 0.6 \n over 1m units at ksh 0.5 \n Feel free to contact cross gate solutions"
          await sentsms(tokenstr,phone,smstext,prevsmsid)          
          return http.client.OK
        if currentsms.list_reply_id=="Purchase":
          smstext="To purchase units, go to mpesa menu: \n 1. Select lipa na mpesa paybill \n 2. Enter business no 477333 \n 3. Company name as Account number \n \n Enter amount then password \n Enjoy with us "
          await sentsms(tokenstr,phone,smstext,prevsmsid)          
          return http.client.OK
        if currentsms.list_reply_id in("Safaricom","Telkom","Airtel","Dedicated","shared","short_code","M_PESA"):
          smstext="Thanks for checking on us \n unfortunately this is being cooked!! "
          await sentsms(tokenstr,phone,smstext,prevsmsid)          
          return http.client.OK
        if currentsms.text_body=="Guide" or currentsms.text_body=="Help":
            rows=[
                    {
                    "id": "Bulk_sms",
                    "title": "Bulk services",
                    "description": "with custom sender id"
                    },
                    {
                    "id": "USSD",
                    "title": "USSD services",
                    "description": "with dedicated or shared codes"
                    },
                    {
                    "id": "short_code",
                    "title": "premium codes",
                    "description": "...two way conversations with shortcode"
                    },
                    {
                    "id": "M_PESA",
                    "title": "M PESA",
                    "description": "M pesa integrations"
                    },
                    {
                    "id": "Airtime",
                    "title": "Airtime",
                    "description": "Airtime purchase"
                    }
                ]
        if currentsms.list_reply_id=="Bulk_sms":
            rows=[
                     {
                    "id": "Rates",
                    "title": "Rates",
                    "description": "Get Rates"
                    },
                    {
                    "id": "Purchase",
                    "title": "Purchase",
                    "description": "How to purchase"
                    }
                ]
                # {
                #     "id": "0-1000",
                #     "title": "Tier 0-1000",
                #     "description": "Rate ksh 1.00"
                #     },
                #     {
                #     "id": "1001-100000",
                #     "title": "Tier 1001-100000",
                #     "description": "Rate ksh 0.80"
                #     },
                #     {
                #     "id": "100001-1000000",
                #     "title": "Tier 100001-1000000",
                #     "description": "Rate ksh 0.70"
                #     },
                #     {
                #     "id": "over-1000000",
                #     "title": "over 1m",
                #     "description": "Rate ksh 0.50"
                #     }
        if currentsms.list_reply_id=="USSD":
            rows=[
                    {
                    "id": "Dedicated",
                    "title": "Dedicated",
                    "description": "like *421#"
                    },
                    {
                    "id": "shared",
                    "title": "shared",
                    "description": "like *421*1#"
                    }
                ]
        if currentsms.list_reply_id=="Airtime":
            rows=[
                    {
                    "id": "Safaricom",
                    "title": "Safaricom",
                    "description": "Safaricom Airtime"
                    },
                    {
                    "id": "Telkom",
                    "title": "Telkom",
                    "description": "Telkom Airtime"
                    },
                    {
                    "id": "Airtel",
                    "title": "Airtel",
                    "description": "Airtel Airtime"
                    }
                ]
        
    bodyobj={
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": phone,
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": {
      "type": "text",
      "text": "Cross Gate Solutions"
    },
    "body": {
      "text": "Our Services"
    },
    "footer": {
      "text": "Check on us"
    },
    "action": {
      "button": "Click",
      "sections": [
        {
          "title": "Select Option",
          "rows": rows
        }
      ]
    }
  }
}   
    
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload1 = json.dumps(bodyobj)
    
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+tokenstr
    }
    print
    print(payload1,headers)
    conn.request("POST", "/v14.0/103570139153202/messages", payload1, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))#
    return payload1

async def update_sent(db:AsyncSession,msg_id:str):
    
    data = {smsinboundmodel.SmsInbound.replied: True}
    #obj_in_data = jsonable_encoder(data, exclude_unset=True)
    try:
        result = await db.execute(
                update(smsinboundmodel.SmsInbound)
                .filter(
                    smsinboundmodel.SmsInbound.sms_id==msg_id
                ).values(data)
                #.filter_by(**kwargs)
            )
        await db.execute("commit")
    except Exception as e: 
        print("Error Found",e)
    
    await db.flush()
    
