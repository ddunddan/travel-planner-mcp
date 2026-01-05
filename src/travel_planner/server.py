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


# FastMCP 서버 인스턴스 생성
mcp = FastMCP(
    name="travel-planner",
    instructions="""여행 계획을 도와주는 MCP 서버입니다.

[중요] Tool 결과 출력 규칙:
- Tool 결과를 요약하지 마세요
- 모든 URL을 클릭 가능한 마크다운 링크로 표시하세요
- 일정, 장소, 예약 링크 등 모든 정보를 그대로 출력하세요

기능: 국내 장소 검색(카카오맵), 국내외 항공권/숙소 예약 링크 생성""",
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
    origin: str = "인천",
    destination: str = "",
    departure_date: str = "",
    return_date: str | None = None,
    adults: int = 1,
    children: int = 0,
    cabin_class: str = "economy",
    direct_only: bool = True
) -> str:
    """
    항공권 예약 링크를 생성합니다. (스카이스캐너, 네이버항공권)
    
    Args:
        origin: 출발지 (기본: "인천")
        destination: 목적지 (필수, 예: "제주", "도쿄", "파리")
        departure_date: 출발일 (필수, YYYY-MM-DD)
        return_date: 귀국일 (선택, 편도면 생략)
        adults: 성인 인원 (기본 1명)
        children: 어린이 인원 (기본 0명)
        cabin_class: "economy", "business", "first" (기본: economy)
        direct_only: 직항만 검색 (기본 True)
    """
    return await _search_flights(
        origin, destination, departure_date, return_date,
        adults, children, cabin_class, direct_only
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
    children: int = 0
) -> str:
    """
    숙소 예약 링크를 생성합니다.
    
    국내: 야놀자, 여기어때
    해외: Booking, Expedia
    
    Args:
        destination: 목적지 (필수, 예: "제주", "도쿄")
        checkin_date: 체크인 (필수, YYYY-MM-DD)
        checkout_date: 체크아웃 (필수, YYYY-MM-DD)
        adults: 성인 인원 (기본 2명)
        rooms: 객실 수 (기본 1개)
        children: 어린이 수 (기본 0명)
    """
    return await _search_hotels(
        destination, checkin_date, checkout_date,
        adults, rooms, children
    )


# ============================================================
# Tool 4: 여행 일정 생성 (숙소 기반 동선)
# ============================================================
@mcp.tool()
async def plan_trip(
    destination: str,
    start_date: str,
    end_date: str,
    accommodation: str = "",
    transport: str = "car",
    themes: list[str] | None = None,
    adults: int = 2
) -> str:
    """
    숙소 위치 기반으로 여행 일정을 생성합니다.
    
    숙소 주변 맛집, 관광지, 카페를 검색하여 동선을 짜줍니다.
    항공권/숙소 예약은 search_flights, search_hotels를 사용하세요.
    
    Args:
        destination: 여행지 (예: "제주", "부산", "강릉")
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        accommodation: 숙소 이름/위치 (예: "제주 라마다호텔", "해운대 파라다이스호텔")
        transport: 이동수단 - "car"(자차/렌트카), "public"(대중교통) (기본: car)
        themes: 여행 테마 (선택, 예: ["맛집", "자연", "카페"])
        adults: 인원 수 (기본 2명)
    """
    return await _plan_trip(destination, start_date, end_date, accommodation, transport, themes, adults)


# ============================================================
# 서버 실행
# ============================================================
if __name__ == "__main__":
    mode = os.getenv("MCP_TRANSPORT", "stdio")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    if mode == "sse" or mode == "http":
        print("🚀 Starting MCP Server in Streamable HTTP mode...")
        print("   URL: http://0.0.0.0:8000/mcp")
        mcp.run(transport="streamable-http")
    else:
        print("🚀 Starting MCP Server in stdio mode...")
        mcp.run()
