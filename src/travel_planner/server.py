"""Travel Planner MCP Server - FastMCP Entry Point

PlayMCP 등록용 MCP 서버 (Remote / Streamable HTTP)
https://playmcp.kakao.com/
"""

import os
import sys
from mcp.server.fastmcp import FastMCP

from .tools.search_places import search_places as _search_places
from .tools.search_flights import search_flights as _search_flights
from .tools.search_hotels import search_hotels as _search_hotels
from .tools.plan_trip import plan_trip as _plan_trip
from .tools.send_kakao import send_to_kakao as _send_to_kakao


# FastMCP 서버 인스턴스 생성
mcp = FastMCP(
    name="travel-planner",
    instructions="여행 계획을 도와주는 MCP 서버입니다. 국내 장소 검색(카카오맵), 국내외 항공권/숙소 예약 링크 생성, 카카오톡 메시지 전송 기능을 제공합니다.",
    host="0.0.0.0",
    port=8000,
)


# ============================================================
# Tool 1: 장소 검색 (국내 전용 - 카카오맵)
# ============================================================
@mcp.tool()
async def search_places(
    destination: str,
    category: str = "관광지",
    count: int = 5
) -> str:
    """
    국내 여행지의 장소를 검색합니다. (카카오맵)
    
    ⚠️ 해외 장소는 지원하지 않습니다.
    
    Args:
        destination: 국내 여행지 (예: "제주", "부산 해운대", "서울 홍대", "서울시 노원구")
        category: "관광지", "맛집", "카페", "쇼핑", "숙소" (기본: "관광지")
        count: 검색 결과 개수 (기본 5개, 최대 10개)
    """
    return await _search_places(destination, category, count)


# ============================================================
# Tool 2: 항공권 검색 (예약 링크 생성)
# ============================================================
@mcp.tool()
async def search_flights(
    destination: str,
    departure_date: str,
    origin: str = "인천",
    return_date: str | None = None,
    adults: int = 1,
    children: int = 0,
    cabin_class: str = "economy",
    direct_only: bool = True,
    count: int = 2,
    site: str | None = None
) -> str:
    """
    항공권 예약 링크를 생성합니다. (스카이스캐너, 네이버항공권)
    
    Args:
        destination: 목적지 (필수, 예: "제주", "도쿄", "파리")
        departure_date: 출발일 (필수, YYYY-MM-DD)
        origin: 출발지 (기본: "인천")
        return_date: 귀국일 (선택, 편도면 생략)
        adults: 성인 인원 (기본 1명)
        children: 어린이 인원 (기본 0명)
        cabin_class: "economy", "business", "first" (기본: economy)
        direct_only: 직항만 검색 (기본 True)
        count: 보여줄 사이트 개수 (기본 2개)
        site: 특정 사이트만 ("skyscanner", "naver", "google")
    """
    return await _search_flights(
        destination, departure_date, origin, return_date,
        adults, children, cabin_class, direct_only, count, site
    )


# ============================================================
# Tool 3: 숙소 검색 (예약 링크 생성)
# ============================================================
@mcp.tool()
async def search_hotels(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0,
    sort_by: str = "popularity",
    breakfast_included: bool = False,
    free_cancellation: bool = False,
    count: int = 4,
    site: str | None = None
) -> str:
    """
    숙소 예약 링크를 생성합니다.
    
    국내: Booking, Agoda, 야놀자, 여기어때
    해외: Booking, Agoda, Hotels.com
    
    Args:
        destination: 목적지 (필수, 예: "제주", "도쿄")
        checkin_date: 체크인 (필수, YYYY-MM-DD)
        checkout_date: 체크아웃 (필수, YYYY-MM-DD)
        adults: 성인 인원 (기본 2명)
        rooms: 객실 수 (기본 1개)
        children: 어린이 수 (기본 0명)
        sort_by: "popularity", "price", "rating", "distance" (기본: popularity)
        breakfast_included: 조식 포함만 (기본 False)
        free_cancellation: 무료 취소만 (기본 False)
        count: 보여줄 사이트 개수 (기본 4개)
        site: 특정 사이트만 ("booking", "agoda", "hotels", "yanolja", "goodchoice")
    """
    return await _search_hotels(
        destination, checkin_date, checkout_date,
        adults, rooms, children, sort_by,
        breakfast_included, free_cancellation, count, site
    )


# ============================================================
# Tool 4: 여행 일정 생성 (종합)
# ============================================================
@mcp.tool()
async def plan_trip(
    destination: str,
    start_date: str,
    end_date: str,
    origin: str = "인천",
    adults: int = 2,
    children: int = 0,
    transport: str = "public",
    themes: list[str] | None = None
) -> str:
    """
    여행 일정을 자동 생성하고 예약 링크를 제공합니다.
    
    국내 여행지: 카카오맵 기반 관광지/맛집/카페 추천 + 예약 링크
    해외 여행지: 예약 링크만 제공
    
    Args:
        destination: 여행지 (예: "제주", "부산", "경주", "도쿄")
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        origin: 출발지 (기본: "인천")
        adults: 성인 인원 (기본 2명)
        children: 어린이 인원 (기본 0명)
        transport: 이동수단 - "car"(자차), "public"(대중교통), "flight"(항공) (기본: public)
        themes: 여행 테마 리스트 (선택, 예: ["자연", "맛집", "카페"])
    """
    return await _plan_trip(destination, start_date, end_date, origin, adults, children, transport, themes)


# ============================================================
# Tool 5: 카카오톡 나에게 보내기
# ============================================================
@mcp.tool()
async def send_to_kakao(
    message: str,
    title: str = "🗺️ 여행 플래너",
    access_token: str | None = None
) -> str:
    """
    여행 일정을 카카오톡 '나에게 보내기'로 전송합니다.
    
    ⚠️ 카카오 로그인 Access Token이 필요합니다.
    
    Args:
        message: 전송할 메시지 내용 (여행 일정 등)
        title: 메시지 제목 (기본: "🗺️ 여행 플래너")
        access_token: 카카오 로그인 Access Token (환경변수 KAKAO_ACCESS_TOKEN으로도 설정 가능)
    """
    return await _send_to_kakao(message, title, access_token)


# ============================================================
# 서버 실행
# ============================================================
if __name__ == "__main__":
    mode = os.getenv("MCP_TRANSPORT", "stdio")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    if mode == "sse" or mode == "http":
        print("🚀 Starting MCP Server in SSE mode...")
        print("   URL: http://0.0.0.0:8000/sse")
        mcp.run(transport="sse")
    else:
        print("🚀 Starting MCP Server in stdio mode...")
        mcp.run()
