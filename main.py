from fastapi import FastAPI
from api.user_api import router as user_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging

# 로깅 설정
logging. basicConfig(
    level=logging.INFO,
    format="%(asctime)s - ticketing-service - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

app = FastAPI()

app.include_router(user_router, prefix="/api/v1", tags=["user"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8001, reload=True)