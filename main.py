from fastapi import FastAPI
from api.user_api import router as user_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging
import os

# Kubernetes 환경에서 파드 및 노드 정보 가져오기
pod_name = os.environ.get("POD_NAME", "unknown-pod")
node_name = os.environ.get("NODE_NAME", "unknown-node")

#"user-service" 전용 로거 생성 (root logger 사용 X)
logger = logging.getLogger("user-service")
logger.setLevel(logging.INFO)


# 중복 핸들러 방지 및 로깅 포맷 설정
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - user-service - %(name)s - %(levelname)s - %(message)s "
        "{pod: %(pod_name)s, node: %(node_name)s}"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False  # root logger로 로그 전파 방지


app = FastAPI()

app.include_router(user_router, prefix="/api/v1", tags=["user"])

@app.get("/health")
async def health_check():
    logger.info("Health check API called", extra={"pod_name": pod_name, "node_name": node_name})
    return {"status": "ok"}

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config=None,  # uvicorn 기본 로깅 비활성화 (root logger 변경 방지)
        log_level="critical"  # uvicorn의 추가 로그 출력을 방지
    )