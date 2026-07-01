from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from app.clients.hospital_client import HospitalDirectoryClient
from app.services.bulk_service import BulkHospitalService
from app.storage.progress_store import progress_store
import csv 
import io
import asyncio
import uuid

router = APIRouter()

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

    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="CSV cannot be empty")

    if(len(rows) > 20):
        raise HTTPException(status_code=400, detail="Maximum 20 records are allowed")
    
    batch_id = str(uuid.uuid4())
    await progress_store.create(batch_id=batch_id, total=len(rows))
    hospital_client = HospitalDirectoryClient(
        base_url="https://hospital-directory.onrender.com"
    )
    bulk_service = BulkHospitalService(
        hospital_client=hospital_client
    )

    asyncio.create_task(
        bulk_service.process_csv_rows(
            batch_id=batch_id,
            hospitals=rows
        )
    )

    return {
        "batch_id": batch_id,
        "status": "accepted",
        "message": "Bulk processing started",
        "status_url": f"/hospitals/bulk/{batch_id}/status",
        "websocket_url": f"/ws/hospitals/bulk/{batch_id}",
    }

@router.get("/hospitals/bulk/{batch_id}/status")
async def get_bulk_status(batch_id: str):
    progress = await progress_store.get(batch_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Batch not found")

    return progress


@router.websocket("/ws/hospitals/bulk/{batch_id}")
async def bulk_progress_websocket(websocket: WebSocket, batch_id: str):
    await websocket.accept()

    try:
        while True:
            progress = await progress_store.get(batch_id)

            if not progress:
                await websocket.send_json({
                    "error": "Batch not found"
                })
                await websocket.close()
                return

            await websocket.send_json(progress)

            if progress["status"] in ["completed", "failed"]:
                await websocket.close()
                return

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        return