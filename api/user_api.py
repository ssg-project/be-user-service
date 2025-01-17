from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from services.user_service import UserService
from dto.dto import *
from utils.database import get_db
from utils.logstash import create_logger
from utils.auth_handler import AuthHandler  # AuthHandler import 추가
import logging
from redis import Redis
import os
from dotenv import load_dotenv

router = APIRouter(prefix='/auth', tags=['user'])
user_logger = create_logger('user-log')
auth_handler = AuthHandler()
redis_client = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

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

        msg = {
            'information': 'ip_browser(request)',
            'message': "scripts.board_find_all(json(session), 'Board Find All')"
        }
        user_logger.info(msg)

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
        
        return {"message": "로그인 성공"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/refresh', description='토큰 갱신')
async def refresh_token(
    response: Response,
    refresh_token_req: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = auth_handler.decode_token(refresh_token_req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="유효하지 않은 refresh token")
        
        user_id = payload.get("user_id")
        
        stored_refresh_token = redis_client.get(f"refresh_token:{user_id}")
        if not stored_refresh_token or stored_refresh_token != refresh_token_req.refresh_token:
            raise HTTPException(status_code=401, detail="만료되었거나 유효하지 않은 토큰")
        
        token_data = {"user_id": user_id, "email": payload.get("email")}
        new_access_token = auth_handler.create_access_token(token_data)
        new_refresh_token = auth_handler.create_refresh_token(token_data)
        
        redis_client.setex(
            f"access_token:{user_id}",
            auth_handler.access_token_expire * 60,
            new_access_token
        )
        redis_client.setex(
            f"refresh_token:{user_id}",
            auth_handler.refresh_token_expire * 60,
            new_refresh_token
        )
        
        return {"message": "토큰 갱신 성공"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post('/logout', description='로그아웃')
def logout(
    refresh_token_req: RefreshTokenRequest,
    response: Response
):
    try:
        payload = auth_handler.decode_token(refresh_token_req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="유효하지 않은 refresh token")
        
        user_id = payload.get("user_id")

        redis_client.delete(f"access_token:{user_id}")
        redis_client.delete(f"refresh_token:{user_id}")

        return {"message": "로그아웃 성공"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@router.post('/withdrawal', description='회원 탈퇴')
def withdrawal(
    request_body: UserDeleteRequest,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    try:
        user_service.delete_db_user(id=request_body.user_id)
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
