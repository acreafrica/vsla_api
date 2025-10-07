# routers/auth.py
from ast import Delete
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import requests
from app.schemas import psplogin as PspLogin
from app.models import PspModel, psppassword as PspPassword,pspmodel as PspModel,vsla_members as vslamember,vslapassword as vslapassword
from app.api.deps.dependencies import get_current_psp   
from app.api.deps.db import get_db_session
from app.api.v1.endpoints.security import hash_password, verify_password, create_access_token,create_reset_token,decode_access_token,generate_otp_code,revoke_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()
@router.post("/logout",tags=['auth'])
async def logout(token: str = Depends(oauth2_scheme)):
    success = revoke_token(token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid token")
    return {"msg": "Logged out successfully"}

@router.post("/login/",tags=['auth'])
async def login(data: PspLogin.PspLogin, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await db.execute(select(PspModel.PspModel).where(PspModel.PspModel.phone_number == data.phone))
        user = result.scalars().first()#.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Account does not exist")

        if user.approval_status != "approved":
            raise HTTPException(status_code=403, detail="Account pending approval")

        result = await db.execute(select(PspPassword.PspPassword).where(PspPassword.PspPassword.psp_id == user.id))
        password_row = result.scalars().first()#.scalar_one_or_none()

        if not password_row or not verify_password(data.password, password_row.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid phone or password")
        
        # we also need to know if a personn is admin or not 
        token = create_access_token(data={"sub": str(user.id), "email": user.email,"usertype": "psp", "is_admin" : user.is_admin})
        return {"access_token": token, "token_type": "bearer", "psp_id": user.id, "psp_name": user.first_name, "admin": user.is_admin}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Something unexpected has occured!!")
        

@router.post("/vsla_login/",tags=['auth'])
async def vsla_login(data: PspLogin.vslaLogin, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(vslamember.Vsla_members).where(vslamember.Vsla_members.phone_number == data.phone))
    user = result.scalars().first()#.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Account does not exist")

    # result = await db.execute(select(vslapassword.VslaPassword).where(vslapassword.VslaPassword.vsla_id == user.id))
    # password_row = result.scalar_one_or_none()
    result = await db.execute(
    select(vslapassword.VslaPassword)
    .where(vslapassword.VslaPassword.vsla_id == user.id)
    .limit(1)
    )
    password_row = result.scalars().first()
    if not password_row:
         otp = generate_otp_code()
         expires_at = datetime.utcnow() + timedelta(minutes=5)

         reset_entry = vslapassword.PspPasswordReset(psp_id=user.id, otp_code=otp, expires_at=expires_at)
         db.add(reset_entry)
         await db.commit()
         message_text = f"Your OTP code is: {otp}. Proceed to reset your password, It expires in 5 minutes."
         try:
                reqUrl = f"http://20.164.220.70:85/digibimaprod/initiatesms?phoneno={data.phone}&message={str(message_text)}"
                # print(reqUrl)
                headersList = {
                "Accept": "*/*",
                "User-Agent": "Thunder Client (https://www.thunderclient.com)"
                }
            
                payload = ""
                response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
                # self.log_error(response.text)
                data = response.json()
                #return data["ResponseCode"] == 1
         except Exception as e:
                return {"msg": "some error occured while sending otp"}
            # TODO: Send SMS with OTP (integrate SMS API)
         print(f"Send OTP {otp} to phone {user.phone_number}")

         return {"msg": "OTP sent to your phone"}
        # print("No password found for user, setting default password")
        # hashed_pwd = hash_password("0000")
        # print(f"Hashed password: {hashed_pwd}")
        # password_row = vslapassword.VslaPassword(vsla_id=user.id, hashed_password=hashed_pwd)
        # db.add(password_row)
        # await db.commit()
        # await db.execute(
        # Delete(vslapassword.VslaPassword).where(vslapassword.VslaPassword.vsla_id == user.id)
        # )
        # hashed_pwd = hash_password("0000")
        # password_row = vslapassword.VslaPassword(vsla_id=user.id, hashed_password=hashed_pwd)
        # db.add(password_row)
        # await db.commit()
    if not password_row or not verify_password(data.password, password_row.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    
    token = create_access_token(data={"sub": str(user.id), "email": user.email,"usertype": "vsla_member", "is_admin" : user.is_admin})
    return {"access_token": token, "token_type": "bearer", "vsla_id": user.vsla_id, "member_id": user.id, "member_type": user.office_position, "member_name": user.member_name}

@router.post("/psp_reset_request/", tags=["auth"])
async def reset_password_psp(data: PspLogin.ResetPasswordRequest, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(PspModel.PspModel).where(PspModel.PspModel.phone_number == data.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    otp = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    reset_entry = vslapassword.PspPasswordReset(psp_id=user.id, otp_code=otp, expires_at=expires_at)
    db.add(reset_entry)
    await db.commit()
    message_text = f"Your OTP code is: {otp}. It expires in 5 minutes."
    try:
            reqUrl = f"http://20.164.220.70:85/digibimaprod/initiatesms?phoneno={data.phone}&message={str(message_text)}"
            # print(reqUrl)
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)"
            }
           
            payload = ""
            response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
            # self.log_error(response.text)
            data = response.json()
            #return data["ResponseCode"] == 1
    except Exception as e:
            return {"msg": "some error occured while sending otp"}
    # TODO: Send SMS with OTP (integrate SMS API)
    print(f"Send OTP {otp} to phone {user.phone_number}")

    return {"msg": "OTP sent to your phone"}

@router.post("/vsla_reset_request/", tags=["auth"])
async def vsla_reset_request(data: PspLogin.VslaResetRequest, db: AsyncSession = Depends(get_db_session)):
    # result = await db.execute(select(vslamember.Vsla_members).where(vslamember.Vsla_members.phone_number == data.phone))
    # user = result.scalar_one_or_none()
    # if not user:
    #     raise HTTPException(status_code=404, detail="Account not found")

    # token = create_reset_token(str(user.id))
    # # TODO: send token via SMS (use SMS API)
    # return {"msg": "Password reset token generated. Check your SMS.", "reset_token": token}
     result = await db.execute(
        select(vslamember.Vsla_members).where(vslamember.Vsla_members.phone_number == data.phone)
    )
     user = result.scalars().first()#scalar_one_or_none()
     if not user:
        raise HTTPException(status_code=404, detail="Account not found")

     otp = generate_otp_code()
     expires_at = datetime.utcnow() + timedelta(minutes=5)

     reset_entry = vslapassword.VslaPasswordReset(vsla_id=user.id, otp_code=otp, expires_at=expires_at)
     db.add(reset_entry)
     await db.commit()
     message_text = f"Your OTP code is: {otp}. It expires in 5 minutes."
     try:
            reqUrl = f"http://20.164.220.70:85/digibimaprod/initiatesms?phoneno={data.phone}&message={str(message_text)}"
            # print(reqUrl)
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)"
            }
           
            payload = ""
            response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
            # self.log_error(response.text)
            data = response.json()
            #return data["ResponseCode"] == 1
     except Exception as e:
            return {"msg": "some error occured while sending otp"}
    # TODO: Send SMS with OTP (integrate SMS API)
     print(f"Send OTP {otp} to phone {user.phone_number}")

     return {"msg": "OTP sent to your phone"}

@router.post("/psp_reset_confirm/", tags=["auth"])
async def reset_password_confirm(data: PspLogin.ResetPasswordConfirm, db: AsyncSession = Depends(get_db_session)):
    # payload = decode_access_token(data.token)
    # if not payload.get("reset"):
    #     raise HTTPException(status_code=400, detail="Invalid reset token")

    # user_id = int(payload["sub"])
    # result = await db.execute(select(PspPassword.PspPassword).where(PspPassword.PspPassword.psp_id == user_id))
    # password_row = result.scalar_one_or_none()
    # if not password_row:
    #     raise HTTPException(status_code=404, detail="Password record not found")

    # password_row.hashed_password = hash_password(data.new_password)
    # db.add(password_row)
    # await db.commit()
    # return {"msg": "Password reset successful"}
    result = await db.execute(
        select(vslapassword.PspPasswordReset).where(vslapassword.PspPasswordReset.otp_code == data.token)
    )
    reset_entry = result.scalars().first()#scalar_one_or_none()

    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    # Find password row
    result = await db.execute(
        select(PspPassword.PspPassword).where(PspPassword.PspPassword.psp_id == reset_entry.psp_id)
    )
    password_row = result.scalars().first()#.scalar_one_or_none()
    if password_row:
        # ✅ Update existing password
        password_row.hashed_password = hash_password(data.new_password)
        db.add(password_row)
    else:
        # ✅ Insert new password record
        new_password_entry = PspPassword.PspPassword(
            psp_id=reset_entry.psp_id,
            hashed_password=hash_password(data.new_password)
            
        )
        db.add(new_password_entry)
    
    # Remove used OTP
    await db.delete(reset_entry)
    await db.commit()

    return {"msg": "Password reset successful"}
    # if not password_row:
    #     raise HTTPException(status_code=404, detail="Password record not found")

    # # Update password
    # password_row.hashed_password = hash_password(data.new_password)
    # db.add(password_row)

    # # Remove used OTP
    # await db.delete(reset_entry)
    # await db.commit()

    # return {"msg": "Password reset successful"}


@router.post("/vsla_reset_confirm/", tags=["auth"])
async def vsla_reset_confirm(data: PspLogin.VslaResetConfirm, db: AsyncSession = Depends(get_db_session)):
    # payload = decode_access_token(data.token)
    # if not payload.get("reset"):
    #     raise HTTPException(status_code=400, detail="Invalid reset token")

    # user_id = int(payload["sub"])
    # result = await db.execute(select(vslapassword.VslaPassword).where(vslapassword.VslaPassword.vsla_id == user_id))
    # password_row = result.scalar_one_or_none()
    # if not password_row:
    #     raise HTTPException(status_code=404, detail="Password record not found")

    # password_row.hashed_password = hash_password(data.new_password)
    # db.add(password_row)
    # await db.commit()
    # return {"msg": "Password reset successful"}
    result = await db.execute(
        select(vslapassword.VslaPasswordReset).where(vslapassword.VslaPasswordReset.otp_code == data.token)
    )
    reset_entry = result.scalars().first()#scalar_one_or_none()

    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    # Find password row
    result = await db.execute(
        select(vslapassword.VslaPassword).where(vslapassword.VslaPassword.vsla_id == reset_entry.vsla_id)
    )
    password_row = result.scalar_one_or_none()
    if password_row:
        # ✅ Update existing password
        password_row.hashed_password = hash_password(data.new_password)
        db.add(password_row)
    else:
        # ✅ Insert new password record
        new_password_entry = vslapassword.VslaPassword(
            vsla_id=reset_entry.vsla_id,
            hashed_password=hash_password(data.new_password)
            
        )
        db.add(new_password_entry)
    
    # Remove used OTP
    await db.delete(reset_entry)
    await db.commit()

    return {"msg": "Password reset successful"}

@router.get("/me",tags=['auth'])
async def get_me(current_user: PspModel = Depends(get_current_psp)):
    return {
        "id": current_user.id,
        "name": f"{current_user.first_name} {current_user.last_name}",
        "email": current_user.email,
    }