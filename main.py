from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from datetime import datetime

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="금융보안 테스트 API (WebSockets 추가됨)",
    description="데이터 로깅, 샘플 응답 및 실시간 웹소켓 통신 API",
    version="1.0.1",
    openapi_version="3.0.3"  # ✅ 중요: 3.0.x로 지정
)


# CORS 허용 (Copilot Studio 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 정적 파일 서빙
app.mount("/.well-known", StaticFiles(directory="static"), name="static")



# 로그 파일 경로 설정
# 컨테이너 환경에서 쓰기 권한이 있는 경로를 사용합니다.
LOG_FILE_PATH = Path("data/log.txt")

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터 디렉토리 생성"""
    # 로그 파일이 저장될 디렉토리가 없으면 생성
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"로그 디렉토리 생성 확인: {LOG_FILE_PATH.parent}")
    # 파일이 없으면 생성
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()
        print(f"로그 파일 생성: {LOG_FILE_PATH}")


# =======================================================
# 기존 REST API 엔드포인트
# =======================================================

@app.get("/insert/{data}", tags=["Data Operations"])
async def insert_data(data: str):
    """
    GET 요청으로 받은 데이터를 'data/log.txt' 파일에 저장합니다.
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] Received Data: {data}\n"
        
        # 파일에 데이터 추가 (append 모드 'a')
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        return JSONResponse(
            status_code=200,
            content={
                "message": "데이터가 성공적으로 저장되었습니다.",
                "inserted_data": data,
                "timestamp": current_time,
                "file": str(LOG_FILE_PATH)
            }
        )
    except IOError as e:
        # 파일 접근 또는 쓰기 오류 발생 시
        raise HTTPException(
            status_code=500, 
            detail=f"파일 쓰기 오류가 발생했습니다: {e}"
        )

@app.get("/read/1", tags=["Data Operations"])
async def read_sample_response_1(): # 함수 이름 수정
    """
    샘플 JSON 응답 1을 출력합니다.
    """
    sample_response = {
        "id": 1,
        "status": "Success",
        "description": "샘플 데이터 읽기 요청에 대한 응답입니다.",
        "security_level": "High",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)


@app.get("/read/2", tags=["Data Operations"])
async def read_sample_response_2(): # 함수 이름 수정
    """
    샘플 JSON 응답 2를 출력합니다.
    """
    sample_response = {
        "id": 2, # ID를 2로 변경하여 차별화
        "status": "Success",
        "description": "testURL",
        "security_level": "High",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)


# =======================================================
# WebSocket 엔드포인트 추가
# =======================================================

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """
    실시간 양방향 통신을 위한 WebSocket 엔드포인트입니다.
    클라이언트가 메시지를 보내면, 서버는 타임스탬프를 붙여 다시 전송(에코)합니다.
    
    연결 주소: ws://[서버 주소]/ws/realtime
    """
    await websocket.accept()
    client_addr = f"{websocket.client.host}:{websocket.client.port}"
    print(f"WS 연결 수락: {client_addr}")
    
    try:
        # 클라이언트에게 최초 연결 성공 메시지 전송
        await websocket.send_json({
            "status": "connected",
            "message": "WebSocket 서버에 성공적으로 연결되었습니다."
        })
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 서버 응답 메시지 구성 (JSON 형식으로 전송)
            response_data = {
                "type": "echo_response",
                "received_data": data,
                "server_timestamp": current_time,
                "message": "서버가 메시지를 받아 시간을 포함하여 다시 전송합니다."
            }
            
            # 클라이언트에게 JSON 데이터 전송
            await websocket.send_json(response_data)
            
    except WebSocketDisconnect:
        # 클라이언트 연결 해제 시 처리
        print(f"WS 연결 해제: {client_addr}")
    except Exception as e:
        # 기타 예외 처리
        print(f"WS 처리 중 오류 발생: {e}")
    finally:
        # 안전하게 연결 종료
        await websocket.close()
