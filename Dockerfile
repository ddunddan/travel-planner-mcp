# Travel Planner MCP Server - Dockerfile
# Remote 배포용 (Streamable HTTP)

FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/
COPY pyproject.toml .

# 패키지 설치
RUN pip install --no-cache-dir -e .

# 환경 변수 (실행 시 오버라이드)
ENV MCP_TRANSPORT=sse
ENV KAKAO_REST_API_KEY=""
ENV GOOGLE_PLACES_API_KEY=""

# 포트 노출
EXPOSE 8000

# SSE 모드로 실행
CMD ["python", "-m", "src.travel_planner.server", "sse"]

