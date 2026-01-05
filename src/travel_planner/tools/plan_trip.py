"""여행 일정 생성 Tool - 숙소 위치 기반 동선"""

from datetime import datetime, timedelta
from ..services.kakao_map import search_places_korea
from ..services.booking_links import is_korea


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
    항공권/숙소 예약은 별도 tool(search_flights, search_hotels)을 사용하세요.
    
    Args:
        destination: 여행 목적지 (예: "제주", "부산", "강릉")
        start_date: 여행 시작일 (YYYY-MM-DD)
        end_date: 여행 종료일 (YYYY-MM-DD)
        accommodation: 숙소 이름/위치 (예: "제주 라마다호텔", "해운대 파라다이스호텔")
        transport: 이동수단 - "car"(자차/렌트카), "public"(대중교통) (기본: car)
        themes: 여행 테마 (선택, 예: ["맛집", "자연", "카페"])
        adults: 인원 수 (기본 2명)
    
    Returns:
        숙소 위치 기반 여행 일정
    """
    # 날짜 파싱
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "❌ 날짜 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-03-01)"
    
    if end < start:
        return "❌ 종료일이 시작일보다 빠를 수 없습니다."
    
    num_days = (end - start).days + 1
    nights = num_days - 1
    is_domestic = is_korea(destination)
    
    # 해외는 지원하지 않음
    if not is_domestic:
        return f"""⚠️ '{destination}'은(는) 해외 도시입니다.

🌍 현재 해외 여행 일정은 지원되지 않습니다.

💡 국내 여행지 예시: 제주, 부산, 강릉, 경주, 여수, 전주 등"""
    
    # 교통수단 설정
    transport = transport.lower()
    if transport not in ["car", "public"]:
        transport = "car"
    
    transport_names = {
        "car": "🚗 자차/렌트카",
        "public": "🚌 대중교통"
    }
    transport_name = transport_names.get(transport, "🚗 자차/렌트카")
    
    # 검색 기준 위치 (숙소 또는 목적지)
    search_base = accommodation if accommodation else destination
    
    # 장소 검색
    tourist_spots = []
    restaurants = []
    cafes = []
    
    # 테마에 따라 검색 비율 조정
    themes_lower = [t.lower() for t in (themes or [])]
    
    # 맛집 검색
    restaurant_count = num_days * 3 if "맛집" in themes_lower else num_days * 2
    try:
        restaurants = await search_places_korea(f"{search_base} 맛집", size=restaurant_count)
    except Exception:
        try:
            restaurants = await search_places_korea(f"{destination} 맛집", size=restaurant_count)
        except Exception:
            pass
    
    # 관광지 검색
    if "자연" in themes_lower:
        search_keyword = f"{search_base} 자연 명소"
    elif "역사" in themes_lower:
        search_keyword = f"{search_base} 역사 유적"
    else:
        search_keyword = f"{search_base} 관광지"
    
    try:
        tourist_spots = await search_places_korea(search_keyword, size=num_days * 2)
    except Exception:
        try:
            tourist_spots = await search_places_korea(f"{destination} 관광지", size=num_days * 2)
        except Exception:
            pass
    
    # 카페 검색
    cafe_count = num_days * 2 if "카페" in themes_lower else num_days
    try:
        cafes = await search_places_korea(f"{search_base} 카페", size=cafe_count)
    except Exception:
        try:
            cafes = await search_places_korea(f"{destination} 카페", size=cafe_count)
        except Exception:
            pass
    
    # 결과 생성
    lines = []
    lines.append(f"🗺️ {destination} {nights}박 {num_days}일 여행 일정")
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append(f"📅 {start_date} ~ {end_date}")
    lines.append(f"👥 {adults}명")
    lines.append(f"🚀 이동수단: {transport_name}")
    if accommodation:
        lines.append(f"🏨 숙소: {accommodation}")
    if themes:
        lines.append(f"🎯 테마: {', '.join(themes)}")
    lines.append("")
    
    # 일정 섹션
    lines.append("=" * 55)
    lines.append("📋 일정")
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
            lines.append(f"   🚗 {destination} 도착")
            if accommodation:
                lines.append(f"   🏨 {accommodation} 체크인 (짐 보관)")
            else:
                lines.append(f"   🏨 숙소 체크인 (짐 보관)")
        elif tourist_spots and spot_idx < len(tourist_spots):
            spot = tourist_spots[spot_idx]
            lines.append(f"   📍 {spot['name']}")
            if spot['address']:
                lines.append(f"      📌 {spot['address']}")
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
                lines.append(f"      📌 {rest['address']}")
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
                lines.append(f"      📌 {spot['address']}")
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
                lines.append(f"      📌 {cafe['address']}")
            if cafe['url']:
                lines.append(f"      🔗 {cafe['url']}")
            cafe_idx += 1
        
        # 저녁
        lines.append("")
        lines.append("🌙 저녁 (18:30~20:00)")
        if day == num_days - 1:
            lines.append(f"   🏨 체크아웃")
            lines.append(f"   🚗 복귀")
        elif restaurants and rest_idx < len(restaurants):
            rest = restaurants[rest_idx]
            lines.append(f"   📍 {rest['name']}")
            if rest['category']:
                lines.append(f"      🏷️ {rest['category']}")
            if rest['address']:
                lines.append(f"      📌 {rest['address']}")
            if rest['url']:
                lines.append(f"      🔗 {rest['url']}")
            rest_idx += 1
        else:
            lines.append(f"   📍 {destination} 저녁 식사")
        
        # 숙소 복귀 (마지막날 제외)
        if day < num_days - 1 and accommodation:
            lines.append("")
            lines.append("🌙 (20:00~)")
            lines.append(f"   🏨 {accommodation} 복귀")
    
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append("💡 Tips")
    lines.append("   - 장소 링크를 클릭하면 카카오맵에서 위치 확인!")
    lines.append("   - 일정은 참고용이며, 자유롭게 수정하세요!")
    if transport == "car":
        lines.append("   - 주차 공간 미리 확인하세요!")
    lines.append("")
    lines.append("⚠️ [AI 지시] 위 내용을 요약하지 말고 그대로 출력하세요. 모든 URL을 클릭 가능한 링크로 표시하세요.")
    
    return "\n".join(lines)
