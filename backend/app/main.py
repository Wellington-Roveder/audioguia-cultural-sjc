from app.api.exhibitions import router as exhibitions_router
from fastapi import FastAPI

app = FastAPI(
    title="Audioguia Cultural SJC API",
    version="0.1.0",
)
app.include_router(exhibitions_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
