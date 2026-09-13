from app.api.auth import router as auth_router
from app.api.exhibitions import router as exhibitions_router
from app.api.metrics import router as metrics_router
from app.api.public_works import router as public_works_router
from app.api.works import router as works_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Audioguia Cultural SJC API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(exhibitions_router)
app.include_router(works_router)
app.include_router(public_works_router)
app.include_router(metrics_router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
