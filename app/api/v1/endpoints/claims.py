from ast import Str
from typing import List
import json
from fastapi.responses import FileResponse
from app.api.deps.dependencies import get_current_psp
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File,Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import claims as crud,vsla as vsla_crud,products as product_crud
from app.models import pspmodel as pspmodel, psppassword as PspPassword,claims as claimmodel
from app.schemas import psp as pspschema, claim as claimschema
from app.api.deps.db import get_db_session
from .security import hash_password
from pathlib import Path
from typing import Literal
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


@router.post("/claim/", response_model=claimschema.claims, tags=['claims'])
async def create_claim(claim_obj: str = Form(...), db: AsyncSession = Depends(get_db_session),medical_report: UploadFile | None = File(None),
    invoice: UploadFile  | None = File(None), burial_cert: UploadFile  | None = File(None), discharge_letter: UploadFile  | None = File(None)):
    claim_data = claimschema.claimCreate(**json.loads(claim_obj))
    vsla_member=await vsla_crud.get_vsla_member_byid(db=db,vsla_id=claim_data.member_id)
    product=await product_crud.get_product(db=db,product_id=claim_data.type_of_claim) 
    print("going to mcheck vsla member",vsla_member)
    if not vsla_member:
        raise HTTPException(status_code=404, detail="Vsla member not found")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
   
    db_claim = await crud.get_claim_per_vsla_member(db=db, vsla_member_id=claim_data.member_id)
    if db_claim:
        raise HTTPException(status_code=400, detail="Claim already registered for this member")
    new_claim = await crud.create_claims(db=db, claim=claim_data,commit=False)
    if not new_claim:
        raise HTTPException(status_code=400, detail="Error creating claim") 
    
    uploaded_files = {}

    for field_name, file in {
        "medical_report": medical_report,
        "invoice": invoice,
        "burial_cert": burial_cert,
        "discharge_letter": discharge_letter
    }.items():
        if file is not None:
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as f:
                f.write(await file.read())
            uploaded_files[field_name] = str(file_path)# expected to save documents
            claim_doc = claimschema.ClaimDocumentCreate(
                claim_id=new_claim.id,
                doc_type=field_name,
                file_url=str(file_path)
            )
            #setattr(clai, field_name, file.filename)
            new_claim_doc=await crud.create_claim_document(db=db,document=claim_doc)
            if not new_claim_doc:
                raise HTTPException(status_code=400, detail=f"Error uploading document: {field_name}")  
            
            
   
    await db.commit()
    return  new_claim

@router.post("/claim_review/", tags=['claims'])
async def review_claim_official(Claimreview:claimschema.ClaimReviewCreate,db: AsyncSession = Depends(get_db_session)):#,claim_id: int,reviewer_id: int,status:str ,comments:str
    db_claim = await crud.get_claims_by_id(db,claim_id=Claimreview.claim_id)
    if db_claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    reviewer= await vsla_crud.get_vsla_member_byid(db,vsla_id=Claimreview.reviewer_id)
    if reviewer is None:
        raise HTTPException(status_code=404, detail="reviewer not found")
    # claim_review = claimschema.ClaimReviewCreate(
    #             claim_id=claim_id,
    #             reviewer_id=reviewer_id,
    #             role=reviewer.office_position,
    #             comments=comments,
    #             status=status

    #         ) 
    db_review = await crud.create_claim_review(db,review=Claimreview,commit=False)
    if db_review is None:       
        raise HTTPException(status_code=400, detail="Error creating review")
    return db_review
@router.post("/claim_approval/", tags=['claims'])
async def claim_approval(claimapproval:claimschema.ClaimApprovalCreate,db: AsyncSession = Depends(get_db_session)):
    db_claim = await crud.get_claims_by_id(db=db,claim_id=claimapproval.claim_id)
    if db_claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    reviewer= await vsla_crud.get_vsla_member_byid(db,vsla_id=claimapproval.approver_id)
    if reviewer is None:
        raise HTTPException(status_code=404, detail="approver not found")
    # claim_obj=claimschema.ClaimApprovalCreate(
    #     claim_id=claim_id,
    #     approver_id=reviewer_id,
    #     comments=comments,
    #     status=status   
    # )
    db_approve = await crud.create_claim_approval(db,approval=claimapproval,commit=False)
    if db_approve is None:       
        raise HTTPException(status_code=400, detail="Error creating app")
    return db_approve

@router.get("/claims/", tags=['claims'])
async def read_claims(skip: int = 0, limit: int = 100,  db: AsyncSession = Depends(get_db_session)):
    claims = await crud.get_claims(db, skip=skip, limit=limit)
    return claims

@router.get("/claim_details/", tags=['claims'])
async def read_claim_details(claim_id,  db: AsyncSession = Depends(get_db_session)):
    claims = await crud.get_claim_details(db, claim_id=claim_id)
    return claims