from ast import Str
from typing import List
import json
from fastapi.responses import FileResponse
from app.api.deps.dependencies import get_current_psp, get_current_user
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File,Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import psp as crud
from app.models import pspmodel as pspmodel, psppassword as PspPassword
from app.schemas import psp as pspschema
from app.api.deps.db import get_db_session
from .security import hash_password
from pathlib import Path
from typing import Literal
from pydantic import ValidationError
UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
#from sql_app.database import SessionLocal, engine


#usermodel.Base.metadata.create_all(bind=engine)

router = APIRouter()
#app = FastAPI()


@router.get("/files/{filename}", tags=["files"])
async def get_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, media_type="application/octet-stream", filename=filename)
    #return FileResponse(file_path)

@router.post("/psp/", response_model=pspschema.pspCreate, tags=['psp'])
async def create_psp( psp_json: str = Form(...), db: AsyncSession = Depends(get_db_session),id_copy: UploadFile | None = File(None),
    cert_file: UploadFile  | None = File(None)):
# async def create_psp(psp: pspschema.pspCreate, db: AsyncSession = Depends(get_db_session),id_copy: UploadFile | None = File(None),
#     cert_file: UploadFile  | None = File(None)):
    try:
        psp_data = pspschema.pspCreate(**json.loads(psp_json))
        #return {"phone_number": psp_data.phone_number, "message": "Valid PSP member"}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Invalid phone number format. Use international format e.g. +2547XXXXXXX")#json.loads(e.json()))
    #psp_data = pspschema.pspCreate(**json.loads(psp_json))
    
   
    db_user = await crud.get_psp_by_phone(db, phone=psp_data.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    uploaded_files = {}

    for field_name, file in {
        "id_copy": id_copy,
        "professional_cert": cert_file
    }.items():
        if file is not None:
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as f:
                f.write(await file.read())
            uploaded_files[field_name] = str(file_path)
            setattr(psp_data, field_name, file.filename)
    print(f"psp_data: {psp_data}")
    new_psp = await crud.create_psp(db=db, psp=psp_data)
    hashed_pwd = hash_password(psp_data.password)
    password_row = PspPassword.PspPassword(psp_id=new_psp.id, hashed_password=hashed_pwd)
    db.add(password_row)
    await db.commit()
    return  new_psp



@router.get("/psp/", response_model=List[pspschema.psp], tags=['psp'])
async def read_psp(status:int=None,skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session),current_user= Depends(get_current_user)):
    print("Current user:", current_user)  
    print("As dict:", current_user.__dict__) 
    if current_user.usertype != "psp":
        raise HTTPException(status_code=403, detail="Only PSP accounts can view this resource")
    psp = await crud.get_psp(db,status=status, skip=skip, limit=limit)
    return psp

@router.post("/aprove_psp/", tags=['psp'])
async def approve_psp_by_id(psp_id: int,status:int ,is_admin :int=0,db: AsyncSession = Depends(get_db_session)):#,current_user = Depends(get_current_user)):
    db_psp = await crud.approve_psp_by_id(db,status=status, id=psp_id,is_admin=is_admin)

    if db_psp is None:
        raise HTTPException(status_code=404, detail="psp not found")
    return db_psp


