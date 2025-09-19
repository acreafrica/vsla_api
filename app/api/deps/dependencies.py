# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.security import decode_access_token
from app.models import PspModel, vsla_members as vslamember
from app.api.deps.db import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_psp(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(select(PspModel).where(PspModel.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    usertype = payload.get("usertype")

    if not user_id or not usertype:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Handle PSP login
    if usertype == "psp":
        result = await db.execute(select(PspModel).where(PspModel.id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="PSP not found")
        user.usertype = "psp"
        return user#{"usertype": "psp", "user": user}

    # Handle VSLA login
    elif usertype == "vsla_member":
        result = await db.execute(select(vslamember.Vsla_members).where(vslamember.Vsla_members.id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="VSLA member not found")
        user.usertype = "vsla_member"
        return user#{"usertype": "vsla_member", "user": user}

    raise HTTPException(status_code=401, detail="Unknown user type")