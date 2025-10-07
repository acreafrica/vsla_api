from ast import Str
from datetime import datetime, timedelta,date
from typing import Any, Dict, List
import json
from fastapi.responses import JSONResponse
from app.api.v1.endpoints.security import generate_otp_code, hash_password, send_sms_via_gateway
from app.crud.claims import get_claim_summary_by_vsla
from app.schemas.claim import ClaimStatusSummary, VslaClaimSummary
from fastapi import Depends, APIRouter, HTTPException, Request, Response, status,UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import vsla as crud,vsla_members as vsla_membersCrud,psp as pspmodel,vsla_contributions as vsla_contributionsCrud,vsla_member_contributions as vslamemberContributioncrud
from app.models import vsla as vslamodel,vslacsvmodel,vsla_members as vsla_membersModel,pspmodel as PspModel,vsla_member_contributions as VslamemberContribution,vsla_contributions as VslaContribution, vslapassword
from app.api.deps.dependencies import get_current_psp, get_current_user 
from app.schemas import vsla as vslaschema,vsla_members as vsla_membersschema,vsla_contributions as vsla_contributionsschema,vsla_member_contributions as vslamembercontributionschema
from app.api.deps.db import get_db_session
import pandas as pd
from pydantic import ValidationError
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_,func

router = APIRouter()
#app = FastAPI()
EXPECTED_COLUMNS = [
    "Group Name", "Country", "Province", "District", "Ward",
    "Member Name", "ID Number", "Phone Number", "Email", "Office Position","DOB"
]

CONTRIBUTIONS_COLUMNS = ["member_phone", "month", "year", "amount"]
VSLA_CONTRIBUTIONS_COLUMNS = ["group_name", "month", "year", "amount"]
VSLA_MEMBERS_COLUMNS = [
    "Member Name", "ID Number", "Phone Number", "Email", "Office Position"
]
@router.post("/vsla/", response_model=vslaschema.Vsla, tags=['vsla'])
async def create_vsla(vsla: vslaschema.VslaCreate, db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    db_vsla = await crud.get_vsla_by_name(db, vsla_name=vsla.vsla_group_name, psp_id=vsla.psp_id)
    psp= await pspmodel.get_psp_by_id(db,id=vsla.psp_id)
    if not psp:
        raise HTTPException(status_code=404, detail="PSP not found")
    if db_vsla:
        raise HTTPException(status_code=400, detail="vsla group Name already registered")
    new_vsla = vslamodel.Vsla(
            vsla_group_name=vsla.vsla_group_name,
            expected_membership_number=vsla.expected_membership_number,
            country=vsla.country,
            province=vsla.province,
            district=vsla.district,
            ward=vsla.ward   ,
            vsla_status="Active" , # Default status
            psp_id=vsla.psp_id  # Associate with current PSP
        )
    return await crud.create_vsla(db=db, vsla=new_vsla,commit=True)

@router.get("/vslas_leaders/", tags=['vsla'])
async def list_vslas_with_leaders(db: AsyncSession = Depends(get_db_session),current_user= Depends(get_current_user)):
    
    # Member = aliased(vsla_membersModel.Vsla_members)

    # # Subquery to pick the first leader (by id, but you could also use created_at or another field)
    # leader_subq = (
    #     select(Member.vsla_id, Member.member_name)
    #     .where(Member.office_position == "Chairperson")
    #     .order_by(Member.id)  # ensures "first" is deterministic
    #     .distinct(Member.vsla_id)  # one per VSLA
    #     .subquery()
    # )

    # # Join VSLA with the leader subquery
    # stmt = (
    #     select(
    #         vslamodel.Vsla.id,
    #         vslamodel.Vsla.vsla_group_name,
    #         leader_subq.c.member_name
    #     )
    #     .outerjoin(leader_subq, leader_subq.c.vsla_id == vslamodel.Vsla.id)
    # )

    # result = await db.execute(stmt)
    # rows = result.all()

    # response = [
    #     {
    #         "vsla_id": vsla_id,
    #         "vsla_name": vsla_name,
    #         "leader": leader_name,
    #     }
    #     for vsla_id, vsla_name, leader_name in rows
    # ]

    # return response
    if current_user.usertype != "psp":
        raise HTTPException(status_code=403, detail="Only PSP accounts can view this resource")
    Member = aliased(vsla_membersModel.Vsla_members)

    # Subquery: assign row numbers per VSLA where office_position is Chairperson
    leader_subq = (
        select(
            Member.vsla_id,
            Member.member_name,
            func.row_number().over(
                partition_by=Member.vsla_id,
                order_by=Member.id
            ).label("rn")
        )
        .where(
        func.lower(Member.office_position).in_(
            ["chairperson", "treasurer", "secretary"]
        )
    )
    .subquery()
    )

    # pick only the first leader per VSLA
    first_leader = (
        select(leader_subq.c.vsla_id, leader_subq.c.member_name)
        .where(leader_subq.c.rn == 1)
        .subquery()
    )

    # Join VSLA with the leader, filter by psp_id from token
    stmt = (
        select(
            vslamodel.Vsla.id,
            vslamodel.Vsla.vsla_group_name,
            first_leader.c.member_name
        )
        .outerjoin(first_leader, first_leader.c.vsla_id == vslamodel.Vsla.id)
        .where(vslamodel.Vsla.psp_id == current_user.id)
    )

    result = await db.execute(stmt)
    rows = result.all()

    response = [
        {
            "vsla_id": vsla_id,
            "vsla_name": vsla_name,
            "leader": leader_name,
        }
        for vsla_id, vsla_name, leader_name in rows
    ]

    return response

@router.get("/vsla/", tags=['vsla'])
async def read_vsla(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session),current_user= Depends(get_current_user)):
   # vsla = await crud.get_all_vsla(db, skip=skip, limit=limit)
    vsla=await crud.get_vsla_per_psp(psp_id=current_user.id, db=db, skip=skip, limit=limit)
    if not vsla:
        raise HTTPException(status_code=404, detail="No VSLA found for the current PSP")
    return vsla
@router.get("/vsla_members/",response_model=List[vsla_membersschema.Vsla_members], tags=['vsla'])
async def read_vsla_members_per_vsla(vsla_id:int,skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session),current_user= Depends(get_current_user)):
   # vsla = await crud.get_all_vsla(db, skip=skip, limit=limit)
    if current_user.usertype == "vsla_member":
        if current_user.id != vsla_id:
            raise HTTPException(status_code=403, detail="Not authorized to view other VSLA members")
    vsla=await crud.get_vsla_members_vsla(vsla_id=vsla_id, db=db, skip=skip, limit=limit)
    if not vsla:
        raise HTTPException(status_code=404, detail="No VSLA_members found for the current vsla")
    return vsla

@router.get("/total_vsla_members/", tags=['vsla'])
async def total_members_vsla(vsla_id:int, db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
   # vsla = await crud.get_all_vsla(db, skip=skip, limit=limit)
    member_count=await crud.get_total_members_vsla(vsla_id=vsla_id, db=db)
    # if not member_count:
    #     raise HTTPException(status_code=404, detail="Some Error Occurred")
    return member_count
def normalize_excel_date(value):
    if not value:
        return None

    # Case 1: Already datetime or pandas Timestamp
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date().isoformat()

    # Case 2: Already a date
    if isinstance(value, date):
        return value.isoformat()

    # Case 3: String from Excel
    if isinstance(value, str):
        value = value.strip()
        # Try common formats
        for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.date().isoformat()
            except ValueError:
                continue
        raise ValueError(f"Unrecognized date format: {value}")

    raise ValueError(f"Unsupported DOB type: {type(value)}")
@router.post("/upload_vsla/", tags=['vsla'])
async def upload_vsla(file: UploadFile = File(...), db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    try:
        if not file.filename.endswith(".xlsx"):
            raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")
        currentpspId= current_user.id
        
        
        # Read Excel
        #df = pd.read_excel(file.file)
        # df = pd.read_excel(file.file, dtype={
        #     "Group Name": str,
        #     "Membership Number": str,
        #     "Country": str,
        #     "Province": str,
        #     "District": str,
        #     "Ward": str,
        #     "Member Name": str,
        #     "ID Number": str,
        #     "Phone Number": str,
        #     "Email": str,
        #     "Office Position": str
        # })

        # # Validate headers
        # missing = set(EXPECTED_COLUMNS) - set(df.columns)
        # if missing:
        #     raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")
        # invalid_rows = []

        # for index, row in df.iterrows():
        #     try:
        #         phone = str(row["Phone Number"]).strip()
        #         if not phone.startswith("+"):
        #             phone = "+" + phone
        #         vsla_membersschema.Vsla_membersCreate(
        #             member_name=row["Member Name"],
        #             id_number=row["ID Number"],
        #             phone_number=phone,
        #             email=row["Email"],
        #             office_position=row["Office Position"],
        #             vsla_id=0,
        #             vsls_id=0
        #         )
        #     except ValidationError as e:
        #         print(f"Validation error in row {index + 2}: {e.errors()}")
        #         phone = row.get("Phone Number", "unknown")
        #     # Generic message including the phone number
        #         invalid_rows.append({
        #             "row": index + 2,  # Excel row number
        #             "errors": [f"Invalid details for phone {phone}"]
        #         })
        #         raise HTTPException(
        #         status_code=400,
        #         detail={
        #             "message": f"Invalid data in Excel at row {index + 2}",
        #             "errors": str(e.errors()),
        #             "phone": phone
        #         }
        #     )

        # # if invalid_rows:
        # #     raise HTTPException(
        # #     status_code=400,
        # #     detail={"message": "Invalid data in Excel", "invalid_rows": invalid_rows}
        # # )
        # for _, row in df.iterrows():
        #     member = vslacsvmodel.Member(
        #         group_name=row["Group Name"],
        #         membership_number=row["Membership Number"],
        #         country=row["Country"],
        #         province=row["Province"],
        #         district=row["District"],
        #         ward=row["Ward"],
        #         member_name=row["Member Name"],
        #         id_number=row["ID Number"],
        #         phone_number=row["Phone Number"],
        #         email=row["Email"],
        #         office_position=row["Office Position"]
        #     )
        #     phone = str(row["Phone Number"]).strip()
        #     if not phone.startswith("+"):
        #         phone = "+" + phone
        #     vsla = vslamodel.Vsla(
        #         vsla_group_name=member.group_name,
        #         expected_membership_number=member.membership_number,
        #         country=member.country,
        #         province=member.province,
        #         district=member.district,
        #         ward=member.ward   ,
        #         vsla_status="active" , # Default status
        #         psp_id=currentpspId  # Associate with current PSP
        #     )
        #     vsla_member_details= vsla_membersModel.Vsla_members(  # Placeholder, will be updated after VSLA creation
        #         member_name=member.member_name,
        #         id_number=member.id_number,
        #         phone_number=phone,
        #         email=member.email,
        #         office_position=member.office_position,vsla_id=0  # Placeholder, will be updated after VSLA creation
        #     )
        #     # vsla_member_schema = vsla_membersschema.Vsla_membersCreate(
        #     #     member_name=member.member_name,
        #     #     id_number=member.id_number,
        #     #     phone_number=member.phone_number,
        #     #     email=member.email,
        #     #     office_position=member.office_position,vsla_id=0  # Placeholder, will be updated after VSLA creation
        #     # )
        #     current_vsla_id=0
        #     vsla_exists = await crud.get_vsla_by_name(db, vsla_name=vsla.vsla_group_name, psp_id=currentpspId)
        #     if vsla_exists:
        #         vsla_member_details.vsla_id = vsla_exists.id
        #         current_vsla_id = vsla_exists.id
        #         print(f"VSLA group {vsla.vsla_group_name} already exists with ID {current_vsla_id}.")
        #        # raise HTTPException(status_code=400, detail=f"VSLA group {vsla.vsla_group_name} already exists.")
        #     else:
        #         vsla = await crud.create_vsla(db=db, vsla=vsla,commit=False)
        #         if not vsla:
        #             print(f"Failed to create VSLA group {vsla.vsla_group_name}.")
        #             #raise HTTPException(status_code=500, detail="Failed to create VSLA group.")
        #         current_vsla_id = vsla.id
        #         vsla_member_details.vsla_id = vsla.id
            
        #     vsla_member_exist=await vsla_membersCrud.get_vsla_by_phone(db=db,vsla_member_phone=vsla_member_details.phone_number,vsla_id=vsla_member_details.vsla_id)
        #     if not vsla_member_exist:
        #         vsla_member = await vsla_membersCrud.create_vsla_members( db=db, vsla_member=vsla_member_details, commit=False)
        #         if not vsla_member:
        #             print(f"Failed to create VSLA member {vsla_member_details.member_name} in VSLA {vsla.vsla_group_name}.")
        #             #raise HTTPException(status_code=500, detail="Failed to create VSLA member.")
        #         #print(f"VSLA member {vsla_member.member_name} created successfully in VSLA {vsla.vsla_group_name}.")
        #     else:
        #         print(f"VSLA member {vsla_member_details.member_name} already exists in VSLA {vsla.vsla_group_name}.")
        #         vsla_updated_member=await crud.update_vsla_member_in_db(db=db,member_id=vsla_member_exist.id,member_update=vsla_membersschema.VslaMemberUpdate(
        #             member_name=vsla_member_details.member_name,
        #             phone_number=vsla_member_details.phone_number,
        #             email=vsla_member_details.email,
        #             office_position=vsla_member_details.office_position
        #         ))
        #     save_vsla_member=vsla_membersCrud


        # await db.commit() 
        # return {"message": "VSLA data uploaded successfully."} 
        current_psp_id = current_user.id
        df = pd.read_excel(file.file, dtype=str)

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        # Step 0: check phone format and schema validation
        members_to_insert = []
        phone_set = set()
        for index, row in df.iterrows():
            phone = str(row["Phone Number"]).strip()
            if not phone.startswith("+"):
                phone = "+" + phone

            # Check duplicate phone in Excel
            if phone in phone_set:
                raise HTTPException(status_code=400, detail=f"Duplicate phone in Excel: {phone}")
            phone_set.add(phone)
            DOB =  normalize_excel_date(row["DOB"])
            try:
                
                member = vsla_membersschema.Vsla_membersCreate(
                    member_name=row["Member Name"].strip(),
                    id_number=str(row["ID Number"]).strip(),
                    phone_number=phone,
                    email=row["Email"].strip(),
                    office_position=row["Office Position"].strip(),
                    vsla_id=0 , # placeholder
                    dob=DOB #str(row["DOB"]).strip()
                )
            except ValidationError as e:
                
                raise HTTPException(
                    status_code=400,
                    detail=f"row: {index + 2} with phone {phone}, errors: {str(e.errors()[0]['msg'])}"
                )

            members_to_insert.append({
                "member": member,
                "group_name": row["Group Name"].strip(),
                "membership_number": row.get("Membership Number", "0"),
                "country": row.get("Country", ""),
                "province": row.get("Province", ""),
                "district": row.get("District", ""),
                "ward": row.get("Ward", "")
            })

        # Step 1: Get existing VSLAs and member phones
        stmt = select(vslamodel.Vsla).where(vslamodel.Vsla.psp_id == currentpspId)
        result = await db.execute(stmt)
        existing_vslas = {v.vsla_group_name.lower(): v for v in result.scalars().all()}

        stmt2 = select(vsla_membersModel.Vsla_members.phone_number)
        # .where(
        #     vsla_membersModel.Vsla_members.psp_id == currentpspId
        # )
        result2 = await db.execute(stmt2)
        existing_phones = set([p[0] for p in result2.all()])

        # Step 2: Prepare VSLA objects and members
        new_vslas = {}
        member_objects = []

        for m in members_to_insert:
            gname_lower = m["group_name"].lower()

            # VSLA existence check
            if gname_lower in existing_vslas:
                vsla_obj = existing_vslas[gname_lower]
            elif gname_lower in new_vslas:
                vsla_obj = new_vslas[gname_lower]
            else:
                vsla_obj = vslamodel.Vsla(
                    vsla_group_name=m["group_name"],
                    expected_membership_number=int(m["membership_number"]),
                    country=m["country"],
                    province=m["province"],
                    district=m["district"],
                    ward=m["ward"],
                    vsla_status="active",
                    psp_id=currentpspId
                )
                db.add(vsla_obj)
                await db.flush()  # ensures id is populated
                new_vslas[gname_lower] = vsla_obj

            # Phone uniqueness check in DB
            if m["member"].phone_number in existing_phones:
                print(f"Phone {m['member'].phone_number} already exists in DB")
                # raise HTTPException(
                #     status_code=400,
                #     detail=f"Phone {m['member'].phone_number} already exists in DB"
                # )
            else:
                existing_phones.add(m["member"].phone_number)

            # Create member object
                member_obj = vsla_membersModel.Vsla_members(
                    member_name=m["member"].member_name,
                    id_number=m["member"].id_number,
                    phone_number=m["member"].phone_number,
                    email=m["member"].email,
                    office_position=m["member"].office_position,
                    vsla_id=vsla_obj.id,
                    dob=m["member"].dob

                )
                member_objects.append(member_obj)
                db.add(member_obj)
                await db.flush()  # to get member_obj.id
                # Generate OTP (temp password)
                otp = generate_otp_code()

                # Store in password table (separate model)
                new_password_entry = vslapassword.VslaPassword(
                vsla_id=member_obj.id,
                hashed_password=hash_password(otp)
                )
                db.add(new_password_entry)
                message=f"Welcome, You have been created as Bima Fund member. Your login phone: {member_obj.phone_number} and OTP/initial password: {otp}. Please change your password after first login."
                await send_sms_via_gateway(
                    phone=member_obj.phone_number,message=message)

        # Step 3: Commit once
        await db.commit()
        return {"message": f"{len(member_objects)} members uploaded successfully."}
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        

@router.post("/upload_vsla_members/", tags=['vsla'])
async def upload_vsla_members(vsla_id:int,file: UploadFile = File(...), db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")
    currentpspId= current_user.id
    
    # Read Excel
    df = pd.read_excel(file.file)

    # Validate headers
    missing = set(VSLA_MEMBERS_COLUMNS) - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")
    invalid_rows = []
    for index, row in df.iterrows():
        try:
            phone = str(row["Phone Number"]).strip()
            if not phone.startswith("+"):
                phone = "+" + phone
            DOB =  normalize_excel_date(row["DOB"])
            vsla_membersschema.Vsla_membersCreate(
                member_name=str(row["Member Name"]).strip(),
                id_number=str(row["ID Number"]).split(".")[0].strip() if row["ID Number"] else None,
                phone_number=str(phone).strip(),
                email=str(row["Email"]).strip() if row["Email"] else None,
                office_position=str(row["Office Position"]).strip() if row["Office Position"] else None,
                dob=DOB,
                vsla_id=0,
                vsls_id=0
               
            )
        except ValidationError as e:
            print(f"Validation error in row {index + 2}: {e.errors()}")
            raise HTTPException(
                status_code=400,
                detail=f"row: {index + 2} with phone {phone}, errors: {str(e.errors()[0]['msg'])}"
            )

        #     phone = row.get("Phone Number", "unknown")
        # # Generic message including the phone number
        #     invalid_rows.append({
        #         "row": index + 2,  # Excel row number
        #         "errors": [f"Invalid details for phone {phone}"]
        #     })
        #     raise HTTPException(
        #     status_code=400,
        #     detail={
        #         "message": f"Invalid data in Excel at row {index + 2}",
        #         "errors": str(e.errors()),
        #         "phone": phone
        #     }
        # )
    # Insert each row
    for _, row in df.iterrows():
        phone = str(row["Phone Number"]).strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        DOB =  normalize_excel_date(row["DOB"])
        member = vslacsvmodel.Member(
            member_name=row["Member Name"],
            id_number=row["ID Number"],
            phone_number=phone,
            email=row["Email"],
            office_position=row["Office Position"]
        )
        vsla_member_details= vsla_membersModel.Vsla_members(  # Placeholder, will be updated after VSLA creation
            member_name=member.member_name,
            id_number=member.id_number,
            phone_number=phone,
            email=member.email,
            dob=DOB,
            office_position=member.office_position,vsla_id=0  # Placeholder, will be updated after VSLA creation
        )
        vsla_exists = await crud.get_vsla_by_id(db, vsla_id=vsla_id)
        if vsla_exists:
            vsla_member_details.vsla_id = vsla_exists.id
           # raise HTTPException(status_code=400, detail=f"VSLA group {vsla.vsla_group_name} already exists.")
        else:
            raise HTTPException(status_code=400, detail=f"VSLA with ID {vsla_id} does not exist.")
           
        vsla_member_exist=await vsla_membersCrud.get_vsla_by_phone(db=db,vsla_member_phone=member.phone_number,vsla_id=vsla_member_details.vsla_id)
        if not vsla_member_exist:
            vsla_member = await vsla_membersCrud.create_vsla_members( db=db, vsla_member=vsla_member_details, commit=False)
            await db.flush()  # to get member_obj.id
            # Generate OTP (temp password)
            otp = generate_otp_code()

            # Store in password table (separate model)
            new_password_entry = vslapassword.VslaPassword(
            vsla_id=vsla_member.id,
            hashed_password=hash_password(otp)
            )
            db.add(new_password_entry)
            message=f"Welcome, You have been created as Bima Fund member. Your login phone: {vsla_member.phone_number} and OTP/initial password: {otp}. Please change your password after first login."
            await send_sms_via_gateway(
                phone=vsla_member.phone_number,message=message)
            if not vsla_member:
                print(f"Failed to create VSLA member {vsla_member_details.member_name} in VSLA {vsla_exists.vsla_group_name}.")
                #raise HTTPException(status_code=500, detail="Failed to create VSLA member.")
            #print(f"VSLA member {vsla_member.member_name} created successfully in VSLA {vsla.vsla_group_name}.")
        else:
            vsla_updated_member=await crud.update_vsla_member_in_db(db=db,member_id=vsla_member_exist.id,member_update=vsla_membersschema.VslaMemberUpdate(
                member_name=vsla_member_details.member_name,
                phone_number=vsla_member_details.phone_number,
                email=vsla_member_details.email,
                office_position=vsla_member_details.office_position,dob=vsla_member_details.dob
            ))
        save_vsla_member=vsla_membersCrud


    await db.commit() 
    return {"message": "VSLA data uploaded successfully."} 
@router.post("/update_vsla_members/", tags=["vsla"])
async def update_vsla_member(
    member_id: int,
    member_update: vsla_membersschema.VslaMemberUpdate,
    db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)
):
    
    vsla_member= await crud.update_vsla_member_in_db(db=db, member_id=member_id, member_update=member_update)

    if not vsla_member:
        raise HTTPException(status_code=404, detail="VSLA member not found")
    return vsla_member
   


@router.post("/upload_contributions/", tags=["vsla"])
async def upload_contributions(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)#,current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    # Read Excel into DataFrame
    df = pd.read_excel(file.file)

    # Validate headers
    missing = set(CONTRIBUTIONS_COLUMNS) - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    
    # for _, row in df.iterrows():
    #     phone = str(row["member_phone"]).strip()
    #     if not phone.startswith("+"):
    #         phone = "+" + phone
    #     month = str(row["month"]).strip()
    #     year = int(row["year"])
    #     amount = float(row["amount"])

    #     result = await db.execute(
    #         select(vsla_membersModel.Vsla_members).where(
    #             vsla_membersModel.Vsla_members.phone_number == phone
    #         )
    #     )
    #     member = result.scalars().first()
    #     if not member:
    #         print(f"Member with phone {phone} not found, skipping...")
    #         continue

    #     result = await db.execute(
    #         select(VslamemberContribution.Vsla_member_contributions).where(
    #             and_(
    #                 VslamemberContribution.Vsla_member_contributions.vsla_member_id == member.id,
    #                 VslamemberContribution.Vsla_member_contributions.month == month,
    #                 VslamemberContribution.Vsla_member_contributions.year == year
    #             )
    #         )
    #     )
    #     existing = result.scalars().first()

    #     # ✅ Use synchronous 'with', not async
    #     with db.no_autoflush:
    #         if existing:
    #             existing.amount = amount
    #         else:
    #             contribution = VslamemberContribution.Vsla_member_contributions(
    #                 vsla_member_id=member.id,
    #                 month=month,
    #                 year=year,
    #                 amount=amount
    #             )
    #             db.add(contribution)
    # await db.commit()
    try:
        for _, row in df.iterrows():
            phone = str(row["member_phone"]).strip()
            if not phone:
                raise HTTPException(status_code=400, detail="❌ Missing phone in Excel")

            if not phone.startswith("+"):
                phone = "+" + phone

            month = str(row["month"]).strip()
            try:
                year = int(row["year"])
                amount = float(row["amount"])
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"❌ Invalid year/amount for {phone}")

            # 🔹 Must exist in vsla_members
            result = await db.execute(
                select(vsla_membersModel.Vsla_members).where(
                    vsla_membersModel.Vsla_members.phone_number == phone
                )
            )
            member = result.scalars().first()
            if not member:
                # 🔥 Stop immediately if phone not found
                raise HTTPException(
                    status_code=400,
                    detail=f"❌ Member with phone {phone} not found in VSLA members list"
                )

            # Check existing contribution
            result = await db.execute(
                select(VslamemberContribution.Vsla_member_contributions).where(
                    and_(
                        VslamemberContribution.Vsla_member_contributions.vsla_member_id == member.id,
                        VslamemberContribution.Vsla_member_contributions.month == month,
                        VslamemberContribution.Vsla_member_contributions.year == year,
                    )
                )
            )
            existing = result.scalars().first()

            with db.no_autoflush:
                if existing:
                    existing.amount = amount
                else:
                    db.add(
                        VslamemberContribution.Vsla_member_contributions(
                            vsla_member_id=member.id,
                            month=month,
                            year=year,
                            amount=amount,
                        )
                    )

        await db.commit()
        return {"message": "Contributions uploaded successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload contributions error: " + str(e))    
@router.post("/upload_vsla_contributions/", tags=["vsla"])
async def upload_vsla_contributions(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    # Read Excel into DataFrame
    df = pd.read_excel(file.file)

    # Validate headers
    missing = set(VSLA_CONTRIBUTIONS_COLUMNS) - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    
    for _, row in df.iterrows():
        group = str(row["group_name"]).strip()
        month = str(row["month"]).strip()
        year = int(row["year"])
        amount = float(row["amount"])

        result = await db.execute(
            select(vslamodel.Vsla).where(
                vslamodel.Vsla.vsla_group_name == group
            )
        )
        group_details = result.scalars().first()
        if not group_details:
            print(f"Member with phone {group} not found, skipping...")
            continue

        result = await db.execute(
            select(VslaContribution.Vsla_contributions).where(
                and_(
                    VslaContribution.Vsla_contributions.vsla_id == group_details.id,
                    VslamemberContribution.Vsla_member_contributions.month == month,
                    VslamemberContribution.Vsla_member_contributions.year == year
                )
            )
        )
        existing = result.scalars().first()

        # ✅ Use synchronous 'with', not async
        with db.no_autoflush:
            if existing:
                existing.amount = amount
            else:
                contribution = VslaContribution.Vsla_contributions(
                    vsla_id=group_details.id,
                    month=month,
                    year=year,
                    amount=amount
                )
                db.add(contribution)
    await db.commit()
    return {"message": "Contributions uploaded successfully."}
@router.get("/vsla_contributions/", tags=["vsla"])#response_model=List[vsla_contributionsschema.Vsla_contributions],
async def get_vsla_contributions(vsla_id:int, db: AsyncSession = Depends(get_db_session)):#,current_user = Depends(get_current_user)):
    contributions = await vsla_contributionsCrud.get_contribution_per_vsla(db=db, vsla_id=vsla_id)
    if not contributions:
        raise HTTPException(status_code=404, detail="No contributions found for the specified VSLA")
    return contributions
@router.get("/vsla_member_contributions/", tags=["vsla"])
async def get_vsla_member_contributions(vsla_id:int, db: AsyncSession = Depends(get_db_session)):#,current_user = Depends(get_current_user)):
    contributions = await vslamemberContributioncrud.get_contribution_per_vsla(db=db, vsla_id=vsla_id)
    if not contributions:
        raise HTTPException(status_code=404, detail="No contributions found for the specified VSLA members")
    return contributions
@router.post("/vsla_contributions/", tags=["vsla"])
async def add_vsla_contribution(contribution: vsla_contributionsschema.Vsla_contributionsCreate,    db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    # Verify member exists
    result = await db.execute(
        select(vslamodel.Vsla).where(
            vslamodel.Vsla.id == contribution.vsla_id
        )
    )
    vsla = result.scalars().first()
    if not vsla:
        raise HTTPException(status_code=404, detail="VSLA member not found")

    new_contribution = VslaContribution.Vsla_contributions(
        vsla_id=contribution.vsla_id,
        month=contribution.month,
        year=contribution.year,
        amount=contribution.amount
    )
    db.add(new_contribution)
    await db.commit()
    await db.refresh(new_contribution)
    return new_contribution

@router.get("/psp/monthly-contributions", tags=["psp"])
async def monthly_contributions(psp_id: int, db: AsyncSession = Depends(get_db_session),current_user = Depends(get_current_user)):
    rows = await vsla_contributionsCrud.get_monthly_contributions(psp_id, db)
    # Convert tuples to list of dicts for JSON response
    data = [{"year": r[0], "month": r[1], "total_contributions": r[2]} for r in rows]
    return data

@router.get("/claim_summary/", response_model=VslaClaimSummary, tags=["claims"])
async def claim_summary(
    vsla_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    summary = await get_claim_summary_by_vsla(db, vsla_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No claims found for this VSLA")
    
    return summary
@router.get("/vsla_details/", response_model=vslaschema.Vsla, tags=["vsla"])
async def get_vsla_by_id(vsla_id: int, db: AsyncSession = Depends(get_db_session)):
    vslas = await crud.get_vsla_by_id( db=db,vsla_id=vsla_id)
    if not vslas:
        raise HTTPException(status_code=404, detail="No data found for this VSLA")
    
    return vslas