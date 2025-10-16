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
        "description": "https://loop.cloud.microsoft/p/eyJ3Ijp7InUiOiJodHRwczovL2hvbWUubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbS8%2FbmF2PWN6MGxNa1ltWkQxaUlVNTRXVzFNZW5waGVXdFRORjh5UjBRNVVUWmliakJGYkVWS1pESXlWMlJPYVdWaVdqazVNMUZ6U1dSRVRIRXRZWFZYUWt0Uk5WaERXR2xSWW10U1MyOG1aajB3TVZwS1EwMVlNMHRMTTBoSFVWVTNTVWxOVGtaYVJsVTNUbEZKU0VSRFNGcFFKbU05Sm1ac2RXbGtQVEUlM0QiLCJyIjpmYWxzZX0sInAiOnsidSI6Imh0dHBzOi8vaG9tZS5taWNyb3NvZnRwZXJzb25hbGNvbnRlbnQuY29tLzpmbDovci9jb250ZW50c3RvcmFnZS9DU1BfMmYyNjE2MzctZGEzYy00NGNhLWI4ZmYtNjE4M2Y1MGU5YjlmL0RvY3VtZW50JTIwTGlicmFyeS9Mb29wQXBwRGF0YS8lRUMlQTAlOUMlRUIlQUElQTklMjAlRUMlOTclODYlRUMlOUQlOEMubG9vcD9kPXc5MzZkMjBkZTdhOTA0YzMzOTAzOTY4ZWM1MjQ5ZjBiZCZjc2Y9MSZ3ZWI9MSZuYXY9Y3owbE1rWmpiMjUwWlc1MGMzUnZjbUZuWlNVeVJrTlRVRjh5WmpJMk1UWXpOeTFrWVROakxUUTBZMkV0WWpobVppMDJNVGd6WmpVd1pUbGlPV1ltWkQxaUlVNTRXVzFNZW5waGVXdFRORjh5UjBRNVVUWmliakJGYkVWS1pESXlWMlJPYVdWaVdqazVNMUZ6U1dSRVRIRXRZWFZYUWt0Uk5WaERXR2xSWW10U1MyOG1aajB3TVZwS1EwMVlNMDgyUlVKWFdraEZSREpIVGtkS1FVOU1TVFZTU2tWVU5FWTFKbU05SlRKR0ptWnNkV2xrUFRFbVlUMU1iMjl3UVhCd0puQTlKVFF3Wm14MWFXUjRKVEpHYkc5dmNDMXdZV2RsTFdOdmJuUmhhVzVsY2laNFBTVTNRaVV5TW5jbE1qSWxNMEVsTWpKVU1GSlVWVWg0YjJJeU1XeE1iVEZ3V1ROS2RtTXlPVzFrU0VKc1kyNU9kbUp0Um5OWk1qbDFaRWRXZFdSRE5XcGlNakU0V1dsR1QyVkdiSFJVU0hBMldWaHNjbFY2VW1aTmEyUkZUMVpGTWxsdE5IZFNWM2hHVTIxUmVVMXNaR3RVYld4c1dXeHZOVTlVVGxKak1HeHJVa1Y0ZUV4WFJqRldNRXBNVlZSV1dWRXhhSEJWVjBweVZXdDBkbVpFUVhoWGEzQkVWRlpuZWxNd2MzcFRSV1JTVmxSa1NsTlZNVTlTYkhCSFZsUmtUMVZWYkVsU1JVNUpWMnhCSlRORUpUSXlKVEpESlRJeWFTVXlNaVV6UVNVeU1tWTJaR1F5TURReExXUXlOV010TkRGaFlpMWhabVpqTFRKalpEUm1NR1UyTUdaaU9DVXlNaVUzUkElM0QlM0QiLCJyIjpmYWxzZX0sImkiOnsiaSI6ImY2ZGQyMDQxLWQyNWMtNDFhYi1hZmZjLTJjZDRmMGU2MGZiOCJ9fQ%3D%3D",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)



@app.get("/read/5", tags=["Data Operations"])
async def read_sample_response():           
    """
    Loop 페이지 링크입니다.
    """
    sample_response = {
        "id": 1,
        "status": "Success",
        "description": "https://loop.cloud.microsoft/p/eyJ3Ijp7InUiOiJodHRwczovL2hvbWUubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbS8%2FbmF2PWN6MGxNa1ltWkQxaUlVNTRXVzFNZW5waGVXdFRORjh5UjBRNVVUWmliakJGYkVWS1pESXlWMlJPYVdWaVdqazVNMUZ6U1dSRVRIRXRZWFZYUWt0Uk5WaERXR2xSWW10U1MyOG1aajB3TVZwS1EwMVlNMHRMTTBoSFVWVTNTVWxOVGtaYVJsVTNUbEZKU0VSRFNGcFFKbU05Sm1ac2RXbGtQVEUlM0QiLCJyIjpmYWxzZX0sInAiOnsidSI6Imh0dHBzOi8vaG9tZS5taWNyb3NvZnRwZXJzb25hbGNvbnRlbnQuY29tLzpmbDovci9jb250ZW50c3RvcmFnZS9DU1BfMmYyNjE2MzctZGEzYy00NGNhLWI4ZmYtNjE4M2Y1MGU5YjlmL0RvY3VtZW50JTIwTGlicmFyeS9Mb29wQXBwRGF0YS8lRUMlQTAlOUMlRUIlQUElQTklMjAlRUMlOTclODYlRUMlOUQlOEMubG9vcD9kPXc5MzZkMjBkZTdhOTA0YzMzOTAzOTY4ZWM1MjQ5ZjBiZCZjc2Y9MSZ3ZWI9MSZuYXY9Y3owbE1rWmpiMjUwWlc1MGMzUnZjbUZuWlNVeVJrTlRVRjh5WmpJMk1UWXpOeTFrWVROakxUUTBZMkV0WWpobVppMDJNVGd6WmpVd1pUbGlPV1ltWkQxaUlVNTRXVzFNZW5waGVXdFRORjh5UjBRNVVUWmliakJGYkVWS1pESXlWMlJPYVdWaVdqazVNMUZ6U1dSRVRIRXRZWFZYUWt0Uk5WaERXR2xSWW10U1MyOG1aajB3TVZwS1EwMVlNMDgyUlVKWFdraEZSREpIVGtkS1FVOU1TVFZTU2tWVU5FWTFKbU05SlRKR0ptWnNkV2xrUFRFbVlUMU1iMjl3UVhCd0puQTlKVFF3Wm14MWFXUjRKVEpHYkc5dmNDMXdZV2RsTFdOdmJuUmhhVzVsY2laNFBTVTNRaVV5TW5jbE1qSWxNMEVsTWpKVU1GSlVWVWg0YjJJeU1XeE1iVEZ3V1ROS2RtTXlPVzFrU0VKc1kyNU9kbUp0Um5OWk1qbDFaRWRXZFdSRE5XcGlNakU0V1dsR1QyVkdiSFJVU0hBMldWaHNjbFY2VW1aTmEyUkZUMVpGTWxsdE5IZFNWM2hHVTIxUmVVMXNaR3RVYld4c1dXeHZOVTlVVGxKak1HeHJVa1Y0ZUV4WFJqRldNRXBNVlZSV1dWRXhhSEJWVjBweVZXdDBkbVpFUVhoWGEzQkVWRlpuZWxNd2MzcFRSV1JTVmxSa1NsTlZNVTlTYkhCSFZsUmtUMVZWYkVsU1JVNUpWMnhCSlRORUpUSXlKVEpESlRJeWFTVXlNaVV6UVNVeU1tWTJaR1F5TURReExXUXlOV010TkRGaFlpMWhabVpqTFRKalpEUm1NR1UyTUdaaU9DVXlNaVUzUkElM0QlM0QiLCJyIjpmYWxzZX0sImkiOnsiaSI6ImY2ZGQyMDQxLWQyNWMtNDFhYi1hZmZjLTJjZDRmMGU2MGZiOCJ9fQ%3D%3D",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return JSONResponse(content=sample_response)