from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audit, evaluate, flags

app = FastAPI(title="Flagpole", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flags.router, prefix="/api/v1", tags=["flags"])
app.include_router(evaluate.router, prefix="/api/v1", tags=["evaluate"])
app.include_router(audit.router, prefix="/api/v1", tags=["history"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
