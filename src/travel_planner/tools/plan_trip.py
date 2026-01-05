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
    
    # 테마에 따라 검색 비율 조정
    themes_lower = [t.lower() for t in (themes or [])]
    
    # 장소 검색 (목적지 기반)
    tourist_spots = []
    restaurants = []
    cafes = []
    
    # 맛집 검색
    restaurant_count = num_days * 3 if "맛집" in themes_lower else num_days * 2
    try:
        restaurants = await search_places_korea(f"{destination} 맛집", size=restaurant_count)
    except Exception:
        pass
    
    # 관광지 검색
    if "자연" in themes_lower:
        search_keyword = f"{destination} 자연 명소"
    elif "역사" in themes_lower:
        search_keyword = f"{destination} 역사 유적"
    else:
        search_keyword = f"{destination} 관광지"
    
    try:
        tourist_spots = await search_places_korea(search_keyword, size=num_days * 2)
    except Exception:
        pass
    
    # 카페 검색
    cafe_count = num_days * 2 if "카페" in themes_lower else num_days
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
    
    # 추천 장소 목록
    lines.append("=" * 55)
    lines.append("📍 추천 장소 목록")
    lines.append("=" * 55)
    lines.append("")
    
    if restaurants:
        lines.append("🍽️ 맛집")
        for i, r in enumerate(restaurants[:6], 1):
            lines.append(f"   {i}. {r['name']}")
            if r['address']:
                lines.append(f"      📌 {r['address']}")
            if r['category']:
                lines.append(f"      🏷️ {r['category']}")
            if r['url']:
                lines.append(f"      🔗 {r['url']}")
        lines.append("")
    
    if tourist_spots:
        lines.append("🏛️ 관광지")
        for i, s in enumerate(tourist_spots[:4], 1):
            lines.append(f"   {i}. {s['name']}")
            if s['address']:
                lines.append(f"      📌 {s['address']}")
            if s['url']:
                lines.append(f"      🔗 {s['url']}")
        lines.append("")
    
    if cafes:
        lines.append("☕ 카페")
        for i, c in enumerate(cafes[:3], 1):
            lines.append(f"   {i}. {c['name']}")
            if c['address']:
                lines.append(f"      📌 {c['address']}")
            if c['url']:
                lines.append(f"      🔗 {c['url']}")
        lines.append("")
    
    lines.append("=" * 55)
    lines.append("")
    
    # AI 지시문 (핵심!)
    if accommodation:
        lines.append(f"""⚠️ [AI 지시] 
위 장소 목록을 바탕으로 {nights}박 {num_days}일 일정을 작성하세요.

🏨 숙소 위치: {accommodation}
- 숙소 위치를 중심으로 가까운 장소끼리 묶어서 동선을 짜세요
- 하루에 맛집 2곳 + 관광지 1~2곳 + 카페 1곳 배치
- 각 Day별로 오전/점심/오후/카페/저녁 시간대로 나눠서 작성
- 장소 이동 시 효율적인 동선 고려
- 모든 장소의 카카오맵 링크를 클릭 가능하게 표시

출력 형식:
📌 Day 1 - 날짜 (요일)
🌅 오전: [장소명] - 주소
🍽️ 점심: [맛집명] - 주소
🌇 오후: [관광지명] - 주소  
☕ 카페: [카페명] - 주소
🌙 저녁: [맛집명] - 주소
...""")
    else:
        lines.append(f"""⚠️ [AI 지시]
위 장소 목록을 바탕으로 {nights}박 {num_days}일 일정을 작성하세요.

- 하루에 맛집 2곳 + 관광지 1~2곳 + 카페 1곳 배치
- 각 Day별로 오전/점심/오후/카페/저녁 시간대로 나눠서 작성
- 모든 장소의 카카오맵 링크를 클릭 가능하게 표시""")
    
    return "\n".join(lines)
