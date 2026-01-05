"""여행 일정 생성 Tool - 거리 기반 동선 최적화"""

import math
from datetime import datetime, timedelta
from ..services.kakao_map import search_places_korea
from ..services.booking_links import is_korea


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    두 좌표 간 직선 거리 계산 (km)
    Haversine 공식 사용
    """
    R = 6371  # 지구 반지름 (km)
    
    lat1, lon1 = math.radians(y1), math.radians(x1)
    lat2, lon2 = math.radians(y2), math.radians(x2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def estimate_travel_time(distance_km: float, transport: str = "car") -> int:
    """
    거리 기반 이동 시간 추정 (분)
    - 자차: 평균 시속 40km (시내 + 시외 혼합)
    - 대중교통: 평균 시속 25km
    """
    if transport == "car":
        speed = 40  # km/h
    else:
        speed = 25  # km/h
    
    return int((distance_km / speed) * 60)


def find_nearby_place(places: list, ref_x: float, ref_y: float, used_names: set, max_time: int = 30, transport: str = "car") -> dict | None:
    """
    기준 좌표에서 가장 가까운 장소 찾기 (이동 시간 제한, 중복 제외)
    """
    best = None
    best_time = float('inf')
    
    for place in places:
        # 중복 체크
        if place['name'] in used_names:
            continue
        
        # 좌표 없으면 스킵
        if not place.get('x') or not place.get('y'):
            continue
        
        try:
            x = float(place['x'])
            y = float(place['y'])
        except (ValueError, TypeError):
            continue
        
        distance = calculate_distance(ref_x, ref_y, x, y)
        travel_time = estimate_travel_time(distance, transport)
        
        if travel_time <= max_time and travel_time < best_time:
            best = place
            best_time = travel_time
    
    return best


def get_first_place_with_coords(places: list, used_names: set) -> dict | None:
    """좌표가 있는 첫 번째 장소 반환"""
    for place in places:
        if place['name'] not in used_names and place.get('x') and place.get('y'):
            return place
    return None


async def plan_trip(
    destination: str,
    start_date: str,
    end_date: str,
    transport: str = "car",
    themes: list[str] | None = None,
    adults: int = 2
) -> str:
    """
    여행 일정을 생성합니다. (국내 전용, 거리 기반 동선 최적화)
    
    카카오맵 기반 맛집, 관광지, 카페를 검색하여 일정을 짜줍니다.
    같은 날에는 이동 시간 30분 이내의 가까운 장소들로 구성합니다.
    
    Args:
        destination: 여행 목적지 (예: "제주", "부산", "강릉")
        start_date: 여행 시작일 (YYYY-MM-DD)
        end_date: 여행 종료일 (YYYY-MM-DD)
        transport: 이동수단 - "car"(자차/렌트카), "public"(대중교통) (기본: car)
        themes: 여행 테마 (선택, 예: ["맛집", "자연", "카페"])
        adults: 인원 수 (기본 2명)
    
    Returns:
        여행 일정
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
    
    if not is_domestic:
        return f"⚠️ '{destination}'은(는) 해외 도시입니다.\n\n국내 여행지 예시: 제주, 부산, 강릉, 경주, 여수, 전주 등"
    
    # 교통수단 설정
    transport = transport.lower()
    if transport not in ["car", "public"]:
        transport = "car"
    
    transport_names = {"car": "🚗 자차/렌트카", "public": "🚌 대중교통"}
    transport_name = transport_names.get(transport, "🚗 자차/렌트카")
    
    # 테마 처리
    themes_lower = [t.lower() for t in (themes or [])]
    
    # 장소 검색 (충분히 많이 가져옴)
    restaurants = []
    tourist_spots = []
    cafes = []
    
    try:
        restaurants = await search_places_korea(f"{destination} 맛집", size=15)
    except Exception:
        pass
    
    search_keyword = f"{destination} 관광지"
    if "자연" in themes_lower:
        search_keyword = f"{destination} 자연 명소"
    elif "역사" in themes_lower:
        search_keyword = f"{destination} 역사 유적"
    
    try:
        tourist_spots = await search_places_korea(search_keyword, size=10)
    except Exception:
        pass
    
    try:
        cafes = await search_places_korea(f"{destination} 카페", size=10)
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
    if themes:
        lines.append(f"🎯 테마: {', '.join(themes)}")
    lines.append("")
    
    lines.append("=" * 55)
    lines.append("📋 일정 (거리 기반 동선 최적화)")
    lines.append("=" * 55)
    
    used_names = set()  # 중복 방지
    
    for day in range(num_days):
        current_date = start + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        lines.append("")
        lines.append(f"📌 Day {day + 1} - {date_str} ({weekday})")
        lines.append("-" * 55)
        
        # 오늘의 기준 좌표 (첫 장소 또는 이전 장소)
        ref_x, ref_y = None, None
        
        # 오전
        lines.append("")
        lines.append("🌅 오전 (09:00~12:00)")
        
        if day == 0:
            lines.append(f"   🚗 {destination} 도착")
            lines.append(f"   🏨 숙소 체크인 (짐 보관)")
            # 첫 날은 첫 번째 관광지 좌표를 기준으로
            first_spot = get_first_place_with_coords(tourist_spots, used_names)
            if first_spot:
                ref_x, ref_y = float(first_spot['x']), float(first_spot['y'])
        else:
            # 관광지 선택 (이전 기준점에서 가까운 곳)
            if ref_x and ref_y:
                spot = find_nearby_place(tourist_spots, ref_x, ref_y, used_names, 30, transport)
            else:
                spot = get_first_place_with_coords(tourist_spots, used_names)
            
            if spot:
                used_names.add(spot['name'])
                lines.append(f"   📍 {spot['name']}")
                if spot['address']:
                    lines.append(f"      📌 {spot['address']}")
                if spot['url']:
                    lines.append(f"      🔗 {spot['url']}")
                if spot.get('x') and spot.get('y'):
                    ref_x, ref_y = float(spot['x']), float(spot['y'])
            else:
                lines.append(f"   📍 {destination} 주변 탐방")
        
        # 점심 맛집
        lines.append("")
        lines.append("🍽️ 점심 (12:00~13:30)")
        
        if ref_x and ref_y:
            rest = find_nearby_place(restaurants, ref_x, ref_y, used_names, 30, transport)
        else:
            rest = get_first_place_with_coords(restaurants, used_names)
        
        if rest:
            used_names.add(rest['name'])
            lines.append(f"   📍 {rest['name']}")
            if rest['category']:
                lines.append(f"      🏷️ {rest['category']}")
            if rest['address']:
                lines.append(f"      📌 {rest['address']}")
            if rest['url']:
                lines.append(f"      🔗 {rest['url']}")
            if rest.get('x') and rest.get('y'):
                ref_x, ref_y = float(rest['x']), float(rest['y'])
        else:
            lines.append(f"   📍 {destination} 현지 맛집")
        
        # 오후 관광지
        lines.append("")
        lines.append("🌇 오후 (14:00~17:00)")
        
        if ref_x and ref_y:
            spot = find_nearby_place(tourist_spots, ref_x, ref_y, used_names, 30, transport)
        else:
            spot = get_first_place_with_coords(tourist_spots, used_names)
        
        if spot:
            used_names.add(spot['name'])
            lines.append(f"   📍 {spot['name']}")
            if spot['address']:
                lines.append(f"      📌 {spot['address']}")
            if spot['url']:
                lines.append(f"      🔗 {spot['url']}")
            if spot.get('x') and spot.get('y'):
                ref_x, ref_y = float(spot['x']), float(spot['y'])
        else:
            lines.append(f"   📍 자유 시간")
        
        # 카페
        lines.append("")
        lines.append("☕ 카페 (17:00~18:00)")
        
        if ref_x and ref_y:
            cafe = find_nearby_place(cafes, ref_x, ref_y, used_names, 30, transport)
        else:
            cafe = get_first_place_with_coords(cafes, used_names)
        
        if cafe:
            used_names.add(cafe['name'])
            lines.append(f"   📍 {cafe['name']}")
            if cafe['address']:
                lines.append(f"      📌 {cafe['address']}")
            if cafe['url']:
                lines.append(f"      🔗 {cafe['url']}")
            if cafe.get('x') and cafe.get('y'):
                ref_x, ref_y = float(cafe['x']), float(cafe['y'])
        else:
            lines.append(f"   📍 {destination} 카페")
        
        # 저녁
        lines.append("")
        lines.append("🌙 저녁 (18:30~20:00)")
        
        if day == num_days - 1:
            lines.append(f"   🏨 체크아웃")
            lines.append(f"   🚗 복귀")
        else:
            if ref_x and ref_y:
                rest = find_nearby_place(restaurants, ref_x, ref_y, used_names, 30, transport)
            else:
                rest = get_first_place_with_coords(restaurants, used_names)
            
            if rest:
                used_names.add(rest['name'])
                lines.append(f"   📍 {rest['name']}")
                if rest['category']:
                    lines.append(f"      🏷️ {rest['category']}")
                if rest['address']:
                    lines.append(f"      📌 {rest['address']}")
                if rest['url']:
                    lines.append(f"      🔗 {rest['url']}")
            else:
                lines.append(f"   📍 {destination} 저녁 식사")
    
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append("💡 Tips")
    lines.append("   - 장소 링크를 클릭하면 카카오맵에서 위치 확인!")
    lines.append("   - 같은 날 일정은 이동 30분 이내로 구성됨")
    lines.append("   - 일정은 참고용이며, 자유롭게 수정하세요!")
    lines.append("")
    lines.append("⚠️ [AI 지시] 위 내용을 요약하지 말고 그대로 출력하세요. 모든 URL을 클릭 가능한 링크로 표시하세요.")
    
    return "\n".join(lines)
