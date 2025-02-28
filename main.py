from fastapi import FastAPI
from api.user_api import router as user_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging
import os

# Kubernetes 환경에서 파드 및 노드 정보 가져오기
pod_name = os.environ.get("POD_NAME", "unknown-pod")
node_name = os.environ.get("NODE_NAME", "unknown-node")


#로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - user-service - %(name)s - %(levelname)s - %(message)s"
        "{pod: %(pod_name)s, node: %(node_name)s}"
    ),
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