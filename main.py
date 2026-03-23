from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from datetime import datetime
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os
from urllib.parse import quote

import feedparser

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="Test",
    description="데이터 로깅, 샘플 응답 및 실시간 웹소켓 통신 API",
    version="1.0.1",
    openapi_version="3.0.3"  # ✅ 중요: 3.0.x로 지정
)

origins = [
    "*"  # 모든 오리진 허용 (개발/테스트 용), 보안상 특정 도메인만 허용하는 것이 좋음
    # Copilot Studio에서 요청하는 도메인을 명시적으로 추가
    # 예: "https://copilotstudio.microsoft.com", "https://copilotstudio-prod.microsoft.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 정적 파일 서빙
app.mount("/.well-known", StaticFiles(directory="static"), name="static")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # ✅ 강제로 3.0.3으로 지정
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


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

from datetime import datetime, timezone, timedelta


from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import feedparser

def get_google_news_context(query: str):
    """
    Google News RSS에서 최신 뉴스만 필터링하여 가져옵니다.
    """
    try:
        stop_words = ["오늘", "최신", "뉴스", "알려줘", "알려주세요", "어때", "어떻게", "날짜"]
        clean_query = query
        for word in stop_words:
            clean_query = clean_query.replace(word, "")
        clean_query = clean_query.strip()

        # ✅ 정제 후 키워드가 너무 짧으면 종합 뉴스 피드 사용
        if len(clean_query) < 2:
            rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
        else:
            rss_url = f"https://news.google.com/rss/search?q={quote(clean_query)}&hl=ko&gl=KR&ceid=KR:ko"

        feed = feedparser.parse(rss_url)
        if not feed.entries:
            return ""

        # ✅ 48시간 이내 뉴스만 필터링
        KST = timezone(timedelta(hours=9))
        now = datetime.now(KST)
        cutoff = now - timedelta(hours=48)

        news_items = []
        for entry in feed.entries[:15]:
            published = entry.get("published_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc).astimezone(KST)
                if pub_dt < cutoff:
                    continue
                time_str = pub_dt.strftime("%m/%d %H:%M")
            else:
                time_str = "날짜 미상"

            # ✅ summary HTML 제거 후 200자까지 활용
            raw_summary = getattr(entry, "summary", "") or ""
            summary = re.sub(r"<[^>]+>", "", raw_summary).strip()
            summary = summary[:200] + "..." if len(summary) > 200 else summary

            # ✅ summary가 제목과 중복이면 제목만 표시
            if summary and summary[:20] not in entry.title[:20]:
                news_items.append(f"[{time_str}] {entry.title}\n  내용: {summary}")
            else:
                news_items.append(f"[{time_str}] {entry.title}")

            if len(news_items) >= 5:
                break

        # 최신 뉴스가 없으면 상위 3개 fallback
        if not news_items:
            for entry in feed.entries[:3]:
                news_items.append(f"- {entry.title}")

        return "\n[최신 뉴스]\n" + "\n".join(news_items)

    except Exception:
        return ""


@app.get("/ai/query", tags=["AI Operations"])
async def ai_query(
    text: str = Query(None, alias="text")
):
    """
    사용자의 질문을 받아 실시간 정보(RSS)와 결합 후 AI 응답을 반환합니다.
    """
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY가 설정되지 않았습니다.")

    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail="질문을 입력해주세요.")

    try:
        # 1. 실시간 정보 필요 여부 확인 및 검색
        search_keywords = ["오늘", "뉴스", "토픽", "현재", "날씨", "최신", "이슈"]
        context = ""
        if any(kw in text for kw in search_keywords):
            context = get_google_news_context(text)

        # 2. ✅ 오늘 날짜를 KST 기준으로 시스템 프롬프트에 주입
        KST = timezone(timedelta(hours=9))
        today_str = datetime.now(KST).strftime("%Y년 %m월 %d일")

        system_prompt = f"당신은 유능한 비서입니다. 오늘 날짜는 {today_str}입니다."
        if context:
            system_prompt += f"\n\n아래 제공된 최신 뉴스를 바탕으로 구체적으로 요약하여 답변하세요.\n{context}"

        # 3. ✅ 올바른 Groq 모델명 사용
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            model="llama-3.3-70b-versatile",  # ✅ openai/gpt-oss-120b → 수정
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            stream=False,
        )

        ai_answer = chat_completion.choices[0].message.content

        return {
            "question": text,
            "answer": ai_answer,
            "has_context": bool(context)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}") 

@app.get("/ai/query2", tags=["AI Operations"])
async def ai_query2(
    # Power Automate의 Key값인 'text'와 일치시킵니다.
    text: str = Query(None, alias="text") 
):
    """
    사용자의 질문(text)을 받아 Groq AI로 응답을 반환합니다.
    Power Automate 호출 예: GET /read/8?text=질문내용
    """
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY가 설정되지 않았습니다.")
    
    # 'text' 매개변수가 비어있는지 확인
    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail="질문(text)을 입력해주세요.")

    try:
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text, # 수신한 text를 AI에게 전달
                },
            ],
            model="openai/gpt-oss-120b",  # 모델명은 사용 가능한 최신 것으로 확인 필요 (예: llama3 등)
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            stream=False,
        )

        ai_answer = chat_completion.choices[0].message.content

        return {
            "question": text,
            "answer": ai_answer,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 중 오류 발생: {str(e)}")


@app.get("/read/8")
async def read_8(question: str):
    """
    사용자의 질문을 받아 Groq AI로 응답을 반환합니다.
    사용 예: GET /read/8?question=안녕하세요
    """
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY가 설정되지 않았습니다.")
    
    if not question or question.strip() == "":
        raise HTTPException(status_code=400, detail="질문을 입력해주세요.")

    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ],
        model="compound-beta-mini",  # groq/ 접두사 제거
        temperature=0.5,
        max_tokens=2048,
        top_p=1,
        stream=False,
    )

    answer = chat_completion.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
    }



@app.get("/read/9")
async def read_9():
    """
    adb.exe 파일을 Base64로 인코딩하여 텍스트로 반환합니다.
    """
    import base64
    from fastapi.responses import PlainTextResponse
    
    file_path = "adb.exe"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="adb.exe 파일을 찾을 수 없습니다.")
    
    with open(file_path, "rb") as f:
        base64_text = base64.b64encode(f.read()).decode('utf-8')
    
    return PlainTextResponse(content=base64_text)



@app.get("/read/json")
async def read_json():
    """
    adb.exe 파일을 Base64로 인코딩하여 JSON으로 반환합니다.
    """
    import base64
    
    file_path = "adb.exe"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="adb.exe 파일을 찾을 수 없습니다.")
    
    with open(file_path, "rb") as f:
        base64_text = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        "filename": "adb.exe",
        "encoding": "base64",
        "data": base64_text
    }


from fastapi import FastAPI, Request
from datetime import datetime


@app.get("/security/test")
async def security_test(request: Request):
    """
    HTTP 요청 패킷을 raw format으로 저장하는 엔드포인트
    """
    
    # 1. Start Line 구성 (Method, Path, HTTP Version)
    # 실제 패킷 형태를 재현하기 위해 구성합니다.
    http_protocol = request.scope.get("type", "HTTP").upper()
    http_version = request.scope.get("http_version", "1.1")
    method = request.method
    path = request.url.path
    if request.url.query:
        path += f"?{request.url.query}"
    
    start_line = f"{method} {path} {http_protocol}/{http_version}\n"

    # 2. Headers 구성
    headers_str = ""
    for key, value in request.headers.items():
        # 헤더 키의 첫 글자를 대문자로 변환하여 가독성 확보 (선택 사항)
        formatted_key = "-".join([part.capitalize() for part in key.split("-")])
        headers_str += f"{formatted_key}: {value}\n"

    # 3. 전체 RAW 데이터 결합
    # 요청 본문(Body)이 있는 경우 아래에 추가할 수 있습니다.
    raw_packet = start_line + headers_str + "\n"

    # 4. /tmp/raw.txt 파일로 저장 (append 모드)
    try:
        with open("/tmp/raw.txt", "a", encoding="utf-8") as f:
            f.write(f"--- Captured at {datetime.now()} ---\n")
            f.write(raw_packet)
            f.write("-" * 40 + "\n\n")
    except Exception as e:
        return {"error": f"File save failed: {str(e)}"}

    return {"message": "Raw packet saved to /tmp/raw.txt", "preview": raw_packet.splitlines()}
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
