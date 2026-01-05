"""여행 계획 생성 Tool - 일정 + 예약 링크"""

from datetime import datetime, timedelta
from ..services.kakao_map import search_places_korea
from ..services.booking_links import (
    get_skyscanner_flight_url,
    get_naver_flight_url,
    get_booking_url,
    get_agoda_url,
    get_yanolja_url,
    get_yeogi_url,
    get_airport_code,
    is_korea,
    AIRPORT_CODES,
)


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
    여행 일정을 자동으로 생성하고 예약 링크를 제공합니다.
    
    국내 여행지는 카카오맵 기반 장소 추천,
    항공권/숙소 예약 링크를 제공합니다.
    
    Args:
        destination: 여행 목적지 (예: "제주", "부산", "경주")
        start_date: 여행 시작일 (YYYY-MM-DD)
        end_date: 여행 종료일 (YYYY-MM-DD)
        origin: 출발 도시 (기본: "인천")
        adults: 성인 인원 (기본 2명)
        children: 어린이 인원 (기본 0명)
        transport: 이동수단 - "car"(자차), "public"(대중교통), "flight"(항공) (기본: public)
        themes: 여행 테마 리스트 (선택, 예: ["자연", "맛집", "카페"])
    
    Returns:
        여행 일정 + 항공권/숙소 예약 링크
    """
    # 날짜 파싱
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "❌ 날짜 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-02-01)"
    
    if end < start:
        return "❌ 종료일이 시작일보다 빠를 수 없습니다."
    
    num_days = (end - start).days + 1
    nights = num_days - 1
    is_domestic = is_korea(destination)
    
    # 해외는 지원하지 않음
    if not is_domestic:
        return f"""⚠️ '{destination}'은(는) 해외 도시입니다.

🌍 현재 해외 여행 일정은 지원되지 않습니다.
   → 항공권: search_flights 사용
   → 숙소: 직접 Booking.com, Agoda 등에서 검색

💡 국내 여행지 예시: 제주, 부산, 강릉, 경주, 여수, 전주 등"""
    
    # 교통수단 설정
    transport = transport.lower()
    if transport not in ["car", "public", "flight"]:
        transport = "public"
    
    # 제주는 항공 필수
    if destination in ["제주"]:
        transport = "flight"
    
    transport_names = {
        "car": "🚗 자차",
        "public": "🚌 대중교통",
        "flight": "✈️ 항공"
    }
    transport_name = transport_names.get(transport, "🚌 대중교통")
    
    # 인원 정보
    pax_info = f"성인 {adults}명"
    if children > 0:
        pax_info += f", 어린이 {children}명"
    
    # 장소 검색 (국내만)
    tourist_spots = []
    restaurants = []
    cafes = []
    
    try:
        tourist_spots = await search_places_korea(f"{destination} 관광지", size=num_days * 2)
    except Exception:
        pass
    
    try:
        restaurants = await search_places_korea(f"{destination} 맛집", size=num_days * 2)
    except Exception:
        pass
    
    try:
        cafes = await search_places_korea(f"{destination} 카페", size=num_days)
    except Exception:
        pass
    
    lines = []
    lines.append(f"🗺️ {destination} 여행 플랜")
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append(f"📅 {start_date} ~ {end_date} ({nights}박 {num_days}일)")
    lines.append(f"👥 {pax_info}")
    lines.append(f"🚀 이동수단: {transport_name}")
    lines.append(f"📍 출발: {origin}")
    if themes:
        lines.append(f"🎯 테마: {', '.join(themes)}")
    lines.append("")
    
    # ========================================
    # 이동 수단 섹션
    # ========================================
    origin_code = get_airport_code(origin)
    dest_code = get_airport_code(destination)
    
    lines.append("=" * 55)
    
    if transport == "flight":
        lines.append("✈️ 항공권 예약")
        lines.append("=" * 55)
        lines.append("")
        lines.append(f"🛫 {origin}({origin_code}) → {destination}({dest_code})")
        lines.append(f"📅 가는 날: {start_date} / 오는 날: {end_date}")
        lines.append("")
        
        # 스카이스캐너
        flight_url = get_skyscanner_flight_url(
            origin_code, dest_code, start_date, end_date, adults, children, 0, "economy", True
        )
        lines.append(f"🟠 스카이스캐너: {flight_url}")
        
        # 네이버 항공권
        naver_url = get_naver_flight_url(
            origin_code, dest_code, start_date, end_date, adults, children, 0, "economy"
        )
        lines.append(f"🟢 네이버 항공권: {naver_url}")
            
    elif transport == "car":
        lines.append("🚗 자차 이동 정보")
        lines.append("=" * 55)
        lines.append("")
        lines.append(f"🚗 {origin} → {destination}")
        lines.append(f"🔗 카카오맵 길찾기: https://map.kakao.com/")
        lines.append("")
        lines.append("💡 자차 여행 팁: 주차 공간 미리 확인하세요!")
        
    elif transport == "public":
        lines.append("🚌 대중교통 이동 정보")
        lines.append("=" * 55)
        lines.append("")
        lines.append(f"🚄 {origin} → {destination}")
        lines.append("")
        lines.append("🔗 예매 사이트:")
        lines.append("   🚄 KTX/SRT: https://www.letskorail.com/")
        lines.append("   🚌 고속버스: https://www.kobus.co.kr/")
    
    # ========================================
    # 숙소 예약 섹션
    # ========================================
    lines.append("")
    lines.append("=" * 55)
    lines.append("🏨 숙소 예약")
    lines.append("=" * 55)
    lines.append("")
    
    lines.append(f"📅 체크인: {start_date} / 체크아웃: {end_date}")
    lines.append(f"🛏️ {nights}박 | {pax_info}")
    lines.append("")
    
    yanolja_url = get_yanolja_url(destination, start_date, end_date, adults)
    lines.append(f"🟣 야놀자: {yanolja_url}")
    
    yeogi_url = get_yeogi_url(destination, start_date, end_date, adults)
    lines.append(f"🔵 여기어때: {yeogi_url}")
    
    booking_url = get_booking_url(destination, start_date, end_date, adults, 1, children)
    lines.append(f"🟠 Booking: {booking_url}")
    
    agoda_url = get_agoda_url(destination, start_date, end_date, adults, 1, children)
    lines.append(f"🔴 Agoda: {agoda_url}")
    
    # ========================================
    # 일정 섹션
    # ========================================
    lines.append("")
    lines.append("=" * 55)
    lines.append("📋 추천 일정")
    lines.append("=" * 55)
    
    spot_idx = 0
    rest_idx = 0
    cafe_idx = 0
    
    for day in range(num_days):
        current_date = start + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        lines.append("")
        lines.append(f"📌 Day {day + 1} - {date_str} ({weekday})")
        lines.append("-" * 55)
        
        # 오전
        lines.append("")
        lines.append("🌅 오전 (09:00~12:00)")
        if day == 0:
            if transport == "flight":
                lines.append(f"   ✈️ {destination} 도착")
            elif transport == "car":
                lines.append(f"   🚗 {origin} 출발 → {destination} 이동")
            else:
                lines.append(f"   🚄 {origin} 출발 → {destination} 이동")
            lines.append(f"   🏨 숙소 체크인 (짐 보관)")
        elif tourist_spots and spot_idx < len(tourist_spots):
            spot = tourist_spots[spot_idx]
            lines.append(f"   📍 {spot['name']}")
            if spot['address']:
                lines.append(f"      주소: {spot['address']}")
            if spot['url']:
                lines.append(f"      🔗 {spot['url']}")
            spot_idx += 1
        else:
            lines.append(f"   📍 {destination} 주변 탐방")
        
        # 점심
        lines.append("")
        lines.append("🍽️ 점심 (12:00~13:30)")
        if restaurants and rest_idx < len(restaurants):
            rest = restaurants[rest_idx]
            lines.append(f"   📍 {rest['name']}")
            if rest['category']:
                lines.append(f"      🏷️ {rest['category']}")
            if rest['address']:
                lines.append(f"      주소: {rest['address']}")
            if rest['url']:
                lines.append(f"      🔗 {rest['url']}")
            rest_idx += 1
        else:
            lines.append(f"   📍 {destination} 현지 맛집")
        
        # 오후
        lines.append("")
        lines.append("🌇 오후 (14:00~17:00)")
        if tourist_spots and spot_idx < len(tourist_spots):
            spot = tourist_spots[spot_idx]
            lines.append(f"   📍 {spot['name']}")
            if spot['address']:
                lines.append(f"      주소: {spot['address']}")
            if spot['url']:
                lines.append(f"      🔗 {spot['url']}")
            spot_idx += 1
        else:
            lines.append(f"   📍 자유 시간")
        
        # 카페 타임
        if cafes and cafe_idx < len(cafes):
            lines.append("")
            lines.append("☕ 카페 (17:00~18:00)")
            cafe = cafes[cafe_idx]
            lines.append(f"   📍 {cafe['name']}")
            if cafe['address']:
                lines.append(f"      주소: {cafe['address']}")
            if cafe['url']:
                lines.append(f"      🔗 {cafe['url']}")
            cafe_idx += 1
        
        # 저녁
        lines.append("")
        lines.append("🌙 저녁 (18:30~20:00)")
        if day == num_days - 1:
            if transport == "flight":
                lines.append(f"   ✈️ {origin} 복귀")
            elif transport == "car":
                lines.append(f"   🚗 {origin} 복귀")
            else:
                lines.append(f"   🚄 {origin} 복귀")
        elif restaurants and rest_idx < len(restaurants):
            rest = restaurants[rest_idx]
            lines.append(f"   📍 {rest['name']}")
            if rest['category']:
                lines.append(f"      🏷️ {rest['category']}")
            if rest['address']:
                lines.append(f"      주소: {rest['address']}")
            if rest['url']:
                lines.append(f"      🔗 {rest['url']}")
            rest_idx += 1
        else:
            lines.append(f"   📍 {destination} 야경 명소 & 저녁 식사")
    
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append("💡 Tips")
    lines.append("   - 예약 링크를 클릭하면 실시간 가격을 확인할 수 있어요!")
    lines.append("   - 장소를 클릭하면 카카오맵에서 위치를 확인할 수 있어요!")
    lines.append("   - 일정은 참고용이며, 자유롭게 수정하세요!")
    
    return "\n".join(lines)
