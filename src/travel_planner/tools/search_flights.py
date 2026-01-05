"""항공권 검색 Tool - 예약 링크 생성"""

from ..services.booking_links import (
    get_skyscanner_flight_url,
    get_naver_flight_url,
    get_google_flights_url,
    get_airport_code,
    is_korea,
)

# 지원하는 항공권 사이트 목록
FLIGHT_SITES = {
    "skyscanner": {"name": "스카이스캐너", "emoji": "🟠", "desc": "전 세계 최저가 비교"},
    "naver": {"name": "네이버 항공권", "emoji": "🟢", "desc": "국내 출발 항공권"},
    "google": {"name": "구글 플라이트", "emoji": "🔵", "desc": "구글 항공권 검색"},
}


async def search_flights(
    destination: str = "",
    departure_date: str = "",
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
    항공권 예약 링크를 생성합니다.
    
    스카이스캐너, 네이버 항공권 링크를 우선 제공합니다.
    링크를 클릭하면 실시간 최저가를 확인하고 직접 예약할 수 있습니다.
    
    Args:
        destination: 목적지 (필수, 예: "제주", "도쿄", "오사카")
        departure_date: 출발일 (필수, YYYY-MM-DD 형식)
        origin: 출발지 (기본값: "인천")
        return_date: 귀국일 (선택, 편도면 생략)
        adults: 성인 인원 (기본 1명)
        children: 어린이 인원 (2-11세, 기본 0명)
        cabin_class: 좌석 등급 - "economy", "business", "first" (기본: economy)
        direct_only: 직항만 검색 (기본 True)
        count: 보여줄 사이트 개수 (기본 2개: 스카이스캐너, 네이버)
        site: 특정 사이트만 보기 ("skyscanner", "naver", "google" 중 선택)
    
    Returns:
        항공권 예약 사이트별 검색 링크
    """
    # 필수 파라미터 검증
    if not destination:
        return "❌ 목적지(destination)를 입력해주세요.\n예: search_flights(destination=\"제주\", departure_date=\"2026-02-01\")"
    
    if not departure_date:
        return "❌ 출발일(departure_date)을 입력해주세요.\n형식: YYYY-MM-DD (예: 2026-02-01)"
    
    # 날짜 형식 검증
    try:
        year, month, day = departure_date.split("-")
        if len(year) != 4 or len(month) != 2 or len(day) != 2:
            raise ValueError()
    except:
        return "❌ 출발일 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-02-01)"
    
    if return_date:
        try:
            year, month, day = return_date.split("-")
            if len(year) != 4 or len(month) != 2 or len(day) != 2:
                raise ValueError()
        except:
            return "❌ 귀국일 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-02-05)"
    
    # 공항 코드 변환
    origin_code = get_airport_code(origin)
    dest_code = get_airport_code(destination)
    
    # 여정 타입
    trip_type = "왕복" if return_date else "편도"
    
    # 좌석 등급 한글
    cabin_names = {
        "economy": "일반석",
        "premiumeconomy": "프리미엄 이코노미",
        "business": "비즈니스",
        "first": "일등석"
    }
    cabin_name = cabin_names.get(cabin_class, "일반석")
    
    # 인원 정보
    pax_info = f"성인 {adults}명"
    if children > 0:
        pax_info += f", 어린이 {children}명"
    
    lines = []
    lines.append("✈️ 항공권 검색")
    lines.append("")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"🛫 {origin} ({origin_code}) → {destination} ({dest_code})")
    lines.append(f"📅 {departure_date}" + (f" ~ {return_date}" if return_date else " (편도)"))
    lines.append(f"👥 {pax_info}")
    lines.append(f"💺 {cabin_name} | {trip_type}" + (" | 직항" if direct_only else " | 경유 포함"))
    lines.append("")
    lines.append("-" * 50)
    lines.append("")
    lines.append("📌 아래 링크를 클릭하여 실시간 가격을 확인하세요!")
    lines.append("")
    
    # 사이트별 링크 생성
    sites_shown = 0
    is_domestic_origin = is_korea(origin) or origin_code in ["ICN", "GMP", "PUS", "CJU", "TAE", "CJJ"]
    
    # 특정 사이트만 요청한 경우
    if site:
        site = site.lower()
        if site not in FLIGHT_SITES:
            return f"❌ 지원하지 않는 사이트입니다.\n지원 사이트: skyscanner, naver, google"
        
        if site == "skyscanner":
            url = get_skyscanner_flight_url(
                origin_code, dest_code, departure_date, return_date,
                adults, children, 0, cabin_class, direct_only
            )
            lines.append(f"🟠 스카이스캐너")
            lines.append(f"   {url}")
        elif site == "naver":
            if not is_domestic_origin:
                return "❌ 네이버 항공권은 국내 출발 항공편만 지원합니다."
            url = get_naver_flight_url(
                origin_code, dest_code, departure_date, return_date,
                adults, children, 0, cabin_class
            )
            lines.append(f"🟢 네이버 항공권")
            lines.append(f"   {url}")
        elif site == "google":
            url = get_google_flights_url(
                origin_code, dest_code, departure_date, return_date,
                adults, cabin_class, direct_only
            )
            lines.append(f"🔵 구글 플라이트")
            lines.append(f"   {url}")
    else:
        # 우선순위: 스카이스캐너 > 네이버 > 구글
        # 1. 스카이스캐너 (항상)
        if sites_shown < count:
            skyscanner_url = get_skyscanner_flight_url(
                origin_code, dest_code, departure_date, return_date,
                adults, children, 0, cabin_class, direct_only
            )
            lines.append("🟠 스카이스캐너 (전 세계 최저가 비교)")
            lines.append(f"   {skyscanner_url}")
            lines.append("")
            sites_shown += 1
        
        # 2. 네이버 항공권 (국내 출발만)
        if sites_shown < count and is_domestic_origin:
            naver_url = get_naver_flight_url(
                origin_code, dest_code, departure_date, return_date,
                adults, children, 0, cabin_class
            )
            lines.append("🟢 네이버 항공권")
            lines.append(f"   {naver_url}")
            lines.append("")
            sites_shown += 1
        
        # 3. 구글 플라이트 (count가 3 이상일 때만)
        if sites_shown < count and count >= 3:
            google_url = get_google_flights_url(
                origin_code, dest_code, departure_date, return_date,
                adults, cabin_class, direct_only
            )
            lines.append("🔵 구글 플라이트")
            lines.append(f"   {google_url}")
            lines.append("")
            sites_shown += 1
    
    lines.append("=" * 50)
    lines.append("")
    lines.append("💡 Tip: 여러 사이트를 비교하면 더 저렴한 항공권을 찾을 수 있어요!")
    
    return "\n".join(lines)
