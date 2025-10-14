# Dockerfile

# 1. Python 공식 이미지 (경량화된 alpine 버전 사용 권장)
FROM python:3.11-slim-buster

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 Python 패키지 설치
# FastAPI와 ASGI 서버인 uvicorn을 설치합니다.
# uvicorn[standard]는 uvicorn과 함께 기타 표준 유틸리티를 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
# 현재 디렉토리의 모든 파일(main.py 포함)을 컨테이너의 /app 디렉토리로 복사
COPY . /app

# 5. 데이터 저장용 디렉토리 생성 (쓰기 권한 확보)
# main.py에서 로그 파일을 저장할 data/ 디렉토리를 미리 생성하고 권한을 설정
RUN mkdir -p /app/data && chmod 777 /app/data

# 6. 포트 노출
# FastAPI는 기본적으로 8000번 포트를 사용합니다.
EXPOSE 8000

# 7. 컨테이너 실행 명령어
# Uvicorn을 사용하여 애플리케이션을 실행합니다.
# - main: main.py 파일
# - app: main.py 파일 내의 FastAPI 인스턴스 변수 이름
# - --host 0.0.0.0: 외부에서 접속 가능하도록 설정
# - --port 8000: 포트 설정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]