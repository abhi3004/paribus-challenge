from fastapi import APIRouter, UploadFile, File, HTTPException
import csv 
import io

router = APIRouter()

@router.post("/hospitals_bulk")
@router.post("/hospitals/bulk")
async def bulk_create_hospitals(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV Files allowed")
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    
    required_headers = {"name", "address"}

    if not required_headers.issubset(set(reader.fieldnames or [])):
        raise HTTPException(status_code=400, detail="Missing required headers name and address columns")
    
    rows = list(reader)

    if(len(rows) > 20):
        raise HTTPException(status_code=400, detail="Maximum 20 records are allowed")
    
    print(rows)
    return {"message": "Success"}
