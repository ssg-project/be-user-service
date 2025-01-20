from fastapi import FastAPI
from api.user_api import router as user_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# # middleware 설정
# app.add_middleware( # cors middleware
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.add_middleware( # session middleware
#     SessionMiddleware,
#     secret_key="your_secret_key", # env 파일로 옮길 예정
# )

# router 설정
app.include_router(user_router, prefix="/api/v1", tags=["user"])

@app.get("/")
async def read_root():
    return {"message": "Hello World"}
