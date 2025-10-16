# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from datetime import datetime

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="금융보안 테스트 API",
    description="데이터 로깅 및 샘플 응답 API",
    version="1.0.0"
)

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
async def read_sample_response():
    """
    샘플 JSON 응답을 출력합니다. (예시 응답)
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
async def read_sample_response():
    """
    샘플 JSON 응답을 출력합니다. (예시 응답)
    """
    sample_response = {
        "id": 1,
        "status": "Success",
        "description": "https://outlook.office.com/bookwithme/user/19d8b0fd07fb46ea8c4cbc1df94a206c@fsisaas.onmicrosoft.com/meetingtype/VY9MweOvIUelXzj9DyCvEw2?bookingcode=3020a097-168b-44b1-a71c-6c91beee888b&anonymous&ep=mlink",
        "security_level": "High",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)



@app.get("/read/3", tags=["Data Operations"])
async def read_sample_response():
    """
    샘플 JSON 응답을 출력합니다. (예시 응답)
    """
    sample_response = {
        "id": 1,
        "status": "Success",
        "description": "    https://teams.microsoft.com/l/meetup-join/19%3ameeting_YTJiNmE4MGEtOTkwOS00NWNiLTkxY2QtNWRkMzQ2M2RmZmRk%40thread.v2/0?context=%7b%22Tid%22%3a%222d73dce3-872e-44a5-bd02-3d05056d011a%22%2c%22Oid%22%3a%22f951410c-a3c4-4769-b2e8-41862e4624e5%22%7d",
        "security_level": "High",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)


@app.get("/read/4", tags=["Data Operations"])
async def read_sample_response():           
    """
    Loop 페이지 링크입니다.
    """
    sample_response = {
        "id": 1,
        "status": "Success",
        "description": "https://home.microsoftpersonalcontent.com/:fl:/g/contentstorage/CSP_2f261637-da3c-44ca-b8ff-6183f50e9b9f/IQLeIG2TkHozTJA5aOxSSfC9ARxZXQ8Gpok3lsxNw7Do2TA?e=d0Qgwz&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF8yZjI2MTYzNy1kYTNjLTQ0Y2EtYjhmZi02MTgzZjUwZTliOWYmZD1iJTIxTnhZbUx6emF5a1M0XzJHRDlRNmJuMEVsRUpkMjJXZE5pZWJaOTkzUXNJZERMcS1hdVdCS1E1WENYaVFia1JLbyZmPTAxWkpDTVgzTzZFQldaSEVEMkdOR0pBT0xJNVJKRVQ0RjUmYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4b2IyMWxMbTFwWTNKdmMyOW1kSEJsY25OdmJtRnNZMjl1ZEdWdWRDNWpiMjE4WWlGT2VGbHRUSHA2WVhsclV6UmZNa2RFT1ZFMlltNHdSV3hGU21ReU1sZGtUbWxsWWxvNU9UTlJjMGxrUkV4eExXRjFWMEpMVVRWWVExaHBVV0pyVWt0dmZEQXhXa3BEVFZnelMwc3pTRWRSVlRkSlNVMU9SbHBHVlRkT1VVbElSRU5JV2xBJTNEJTIyJTJDJTIyaSUyMiUzQSUyMmY2ZGQyMDQxLWQyNWMtNDFhYi1hZmZjLTJjZDRmMGU2MGZiOCUyMiU3RA%3D%3D",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)