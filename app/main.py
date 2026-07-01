from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.hospitals_bulk import router as hospitals_router

app = FastAPI(
    title="Hospital Bulk Processing API",
    version="1.0.0",
    description="Bulk CSV processing service for Hospital Directory API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hospitals_router, tags=["Hospitals Bulk"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
