from fastapi import FastAPI

app = FastAPI(
    title="Audioguia Cultural SJC API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
