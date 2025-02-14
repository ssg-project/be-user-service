from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header
from sqlalchemy.orm import Session
from services.user_service import UserService
from dto.dto import *
from utils.database import get_db
from utils.auth_handler import AuthHandler  # AuthHandler import 추가
import logging
from redis import Redis
import os
import json

router = APIRouter(prefix='/auth', tags=['user'])
auth_handler = AuthHandler()
redis_client = Redis(
    host=os.getenv('REDIS_HOST', '127.0.0.1'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

async def get_current_user(request: Request):
    scope_data = request.headers.get("X-Scope")

    if not scope_data:
        raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")
    try:
        scope = json.loads(scope_data)
        user = scope.get("user")
        if not user or not user.get('is_authenticated'):
            raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")
        return user
    except:
        raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")

@router.post('/join', description='회원 가입')
async def join(
    request: Request,
    request_body: UserJoinRequest,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    try:
        # 사용자 등록
        user_service.insert_db_user(email=request_body.email, password=request_body.password)

        # 성공 응답
        return
    
    except Exception as e:
        # 비동기 로그 기록 (실패 시 상태 400)
        # create_logger(
        #     'user-log',
        #     service_name="user_api",
        #     environment="prod",
        #     client_ip=request.client.host,
        #     request_url=str(request.url.path),
        #     request_body=str(request_body),
        #     status=400,
        # )

        # 예외를 HTTPException으로 처리
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/login', description='로그인')
async def login(
    response: Response,
    request_body: UserLoginReqeust,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    try:
        user = user_service.get_user_by_email(email=request_body.email)
        if not user or user.password != request_body.password:
            raise HTTPException(status_code=401, detail="로그인 실패")
        
        token_data = {
            "user_id": user.user_id,
            "email": user.email
        }

        access_token = auth_handler.create_access_token(token_data)
        refresh_token = auth_handler.create_refresh_token(token_data)
        
        redis_client.setex(
            f"access_token:{user.user_id}",
            auth_handler.access_token_expire * 60,
            access_token
        )
        redis_client.setex(
            f"refresh_token:{user.user_id}",
            auth_handler.refresh_token_expire * 60,
            refresh_token
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=auth_handler.refresh_token_expire * 60
        )
        
        return {
            "user_id": user.user_id,
            "user_email": user.email,
            "access_token" : access_token,
            "message": "로그인 성공"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/refresh', description='토큰 갱신')
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request)
    try:
        
        token_data = {"user_id": current_user["user_id"], "email": current_user["email"]}
        new_access_token = auth_handler.create_access_token(token_data)
        new_refresh_token = auth_handler.create_refresh_token(token_data)
        
        redis_client.setex(
            f"access_token:{current_user['user_id']}",
            auth_handler.access_token_expire * 60,
            new_access_token
        )
        redis_client.setex(
            f"refresh_token:{current_user['user_id']}",
            auth_handler.refresh_token_expire * 60,
            new_refresh_token
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=auth_handler.refresh_token_expire * 60
        )
        
        return {
            "access_token" : new_access_token,
            "message": "토큰 갱신 성공"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post('/logout', description='로그아웃')
async def logout(
    request: Request
):
    current_user = await get_current_user(request)
    try:

        redis_client.delete(f"access_token:{current_user['user_id']}")
        redis_client.delete(f"refresh_token:{current_user['user_id']}")

        return {"message": "로그아웃 성공"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@router.post('/withdrawal', description='회원 탈퇴')
async def withdrawal(
    request: Request,
    request_body: UserDeleteRequest,
    db: Session = Depends(get_db),
):
    current_user = await get_current_user(request)
    if str(request_body.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    user_service = UserService(db)

    try:
        user_service.delete_db_user(id=request_body.user_id)
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
