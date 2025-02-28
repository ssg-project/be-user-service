from fastapi import FastAPI
from api.user_api import router as user_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging
import os

# Kubernetes 환경에서 파드 및 노드 정보 가져오기
pod_name = os.environ.get("POD_NAME", "unknown-pod")
node_name = os.environ.get("NODE_NAME", "unknown-node")

# "user-service" 전용 로거 생성 (root logger 사용 X)
logger = logging.getLogger("user-service")
logger.setLevel(logging.INFO)

# 중복 핸들러 방지 및 로깅 포맷 설정
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    
    # pod_name과 node_name을 직접 포함하는 포맷터 적용
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        f"{{pod: {pod_name}, node: {node_name}}}"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False  # root logger로 로그 전파 방지

app = FastAPI()

# API 라우터 등록
app.include_router(user_router, prefix="/api/v1", tags=["user"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Prometheus Instrumentation
@app.on_event("startup")
async def enable_metrics():
    Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config=None,  # Uvicorn 기본 로깅 비활성화
        log_level="info"  # 기존의 "critical" 대신 "info" 유지
    )
