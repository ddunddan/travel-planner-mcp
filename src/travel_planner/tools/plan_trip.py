"""여행 일정 생성 Tool - 카카오모빌리티 API 기반 동선 최적화"""

from datetime import datetime, timedelta
from ..services.kakao_map import search_places_korea
from ..services.kakao_mobility import get_travel_time, get_kakao_directions_url
from ..services.booking_links import is_korea


def calc_distance(ref_x: float, ref_y: float, x: float, y: float) -> float:
    """직선 거리 계산 (km)"""
    import math
    R = 6371
    lat1, lon1 = math.radians(ref_y), math.radians(ref_x)
    lat2, lon2 = math.radians(y), math.radians(x)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


async def find_nearby_place(
    places: list,
    ref_x: float,
    ref_y: float,
    used_names: set,
    max_time: int = 30
) -> tuple[dict | None, int | None]:
    """
    기준 좌표에서 가장 가까운 장소 찾기
    
    1단계: 직선 거리로 가까운 5개 필터링
    2단계: 5개에 대해서만 카카오모빌리티 API 호출
    
    Returns:
        (장소, 이동시간) 튜플
    """
    # 1단계: 직선 거리로 후보 필터링
    candidates = []
    for place in places:
        if place['name'] in used_names:
            continue
        if not place.get('x') or not place.get('y'):
            continue
        try:
            x = float(place['x'])
            y = float(place['y'])
            distance = calc_distance(ref_x, ref_y, x, y)
            candidates.append((place, distance))
        except (ValueError, TypeError):
            continue
    
    # 거리 기준 정렬 후 상위 5개만
    candidates.sort(key=lambda c: c[1])
    top_candidates = candidates[:5]
    
    if not top_candidates:
        return (None, None)
    
    # 2단계: 상위 5개에 대해서만 API 호출
    best = None
    best_time = float('inf')
    
    for place, distance in top_candidates:
        x = float(place['x'])
        y = float(place['y'])
        
        # 카카오모빌리티 API로 실제 이동 시간 계산
        travel_time = await get_travel_time(ref_x, ref_y, x, y)
        
        # API 실패 시 직선 거리로 추정 (시속 40km 가정)
        if travel_time is None:
            travel_time = int((distance / 40) * 60)
        
        if travel_time <= max_time and travel_time < best_time:
            best = place
            best_time = travel_time
    
    # 30분 이내 장소가 없으면 가장 가까운 장소 선택
    if best is None and top_candidates:
        best = top_candidates[0][0]
        distance = top_candidates[0][1]
        best_time = int((distance / 40) * 60)
    
    return (best, int(best_time) if best else None)


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
    여행 일정을 생성합니다. (국내 전용, 실제 이동 시간 기반)
    
    카카오모빌리티 API로 실제 이동 시간을 계산하여
    30분 이내의 가까운 장소들로 동선을 최적화합니다.
    
    Args:
        destination: 여행 목적지 (예: "제주", "부산", "강릉")
        start_date: 여행 시작일 (YYYY-MM-DD)
        end_date: 여행 종료일 (YYYY-MM-DD)
        transport: 이동수단 - "car"(자차/렌트카), "public"(대중교통) (기본: car)
        themes: 여행 테마 (선택, 예: ["맛집", "자연", "카페"])
        adults: 인원 수 (기본 2명)
    
    Returns:
        여행 일정 + 길찾기 링크
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
    
    # 최대 2박 3일 제한 (API 호출 최적화)
    if num_days > 3:
        return "⚠️ 현재 최대 2박 3일까지 일정 생성이 가능합니다.\n\n더 긴 여행은 여러 번 나눠서 요청해주세요!\n예: 1~3일, 4~6일"
    
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
    
    # 장소 검색
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
    lines.append("📋 일정 (이동 30분 이내 동선)")
    lines.append("=" * 55)
    
    used_names = set()
    prev_place = None  # 이전 장소 정보
    
    for day in range(num_days):
        current_date = start + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        lines.append("")
        lines.append(f"📌 Day {day + 1} - {date_str} ({weekday})")
        lines.append("-" * 55)
        
        ref_x, ref_y = None, None
        
        # 오전
        lines.append("")
        lines.append("🌅 오전 (09:00~12:00)")
        
        if day == 0:
            lines.append(f"   🚗 {destination} 도착")
            lines.append(f"   🏨 숙소 체크인 (짐 보관)")
            first_spot = get_first_place_with_coords(tourist_spots, used_names)
            if first_spot:
                ref_x, ref_y = float(first_spot['x']), float(first_spot['y'])
                prev_place = first_spot
        else:
            if ref_x and ref_y:
                spot, travel_min = await find_nearby_place(tourist_spots, ref_x, ref_y, used_names, 30)
            else:
                spot = get_first_place_with_coords(tourist_spots, used_names)
                travel_min = None
            
            if spot:
                used_names.add(spot['name'])
                lines.append(f"   📍 {spot['name']}")
                if spot['address']:
                    lines.append(f"      📌 {spot['address']}")
                if spot['url']:
                    lines.append(f"      🔗 {spot['url']}")
                
                # 길찾기 링크
                if prev_place and spot.get('x') and spot.get('y'):
                    nav_url = get_kakao_directions_url(
                        prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                        spot['name'], float(spot['x']), float(spot['y']),
                        transport
                    )
                    time_str = f" ({travel_min}분)" if travel_min else ""
                    lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                
                if spot.get('x') and spot.get('y'):
                    ref_x, ref_y = float(spot['x']), float(spot['y'])
                    prev_place = spot
            else:
                lines.append(f"   📍 {destination} 주변 탐방")
        
        # 점심 맛집
        lines.append("")
        lines.append("🍽️ 점심 (12:00~13:30)")
        
        rest = None
        travel_min = None
        if ref_x and ref_y:
            rest, travel_min = await find_nearby_place(restaurants, ref_x, ref_y, used_names, 30)
        if not rest:
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
            
            if prev_place and rest.get('x') and rest.get('y'):
                nav_url = get_kakao_directions_url(
                    prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                    rest['name'], float(rest['x']), float(rest['y']),
                    transport
                )
                time_str = f" ({travel_min}분)" if travel_min else ""
                lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
            
            if rest.get('x') and rest.get('y'):
                ref_x, ref_y = float(rest['x']), float(rest['y'])
                prev_place = rest
        else:
            lines.append(f"   📍 {destination} 현지 맛집")
        
        # 오후 관광지
        lines.append("")
        lines.append("🌇 오후 (14:00~17:00)")
        
        spot = None
        travel_min = None
        if ref_x and ref_y:
            spot, travel_min = await find_nearby_place(tourist_spots, ref_x, ref_y, used_names, 30)
        if not spot:
            spot = get_first_place_with_coords(tourist_spots, used_names)
        
        if spot:
            used_names.add(spot['name'])
            lines.append(f"   📍 {spot['name']}")
            if spot['address']:
                lines.append(f"      📌 {spot['address']}")
            if spot['url']:
                lines.append(f"      🔗 {spot['url']}")
            
            if prev_place and spot.get('x') and spot.get('y'):
                nav_url = get_kakao_directions_url(
                    prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                    spot['name'], float(spot['x']), float(spot['y']),
                    transport
                )
                time_str = f" ({travel_min}분)" if travel_min else ""
                lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
            
            if spot.get('x') and spot.get('y'):
                ref_x, ref_y = float(spot['x']), float(spot['y'])
                prev_place = spot
        else:
            lines.append(f"   📍 자유 시간")
        
        # 카페
        lines.append("")
        lines.append("☕ 카페 (17:00~18:00)")
        
        cafe = None
        travel_min = None
        if ref_x and ref_y:
            cafe, travel_min = await find_nearby_place(cafes, ref_x, ref_y, used_names, 30)
        if not cafe:
            cafe = get_first_place_with_coords(cafes, used_names)
        
        if cafe:
            used_names.add(cafe['name'])
            lines.append(f"   📍 {cafe['name']}")
            if cafe['address']:
                lines.append(f"      📌 {cafe['address']}")
            if cafe['url']:
                lines.append(f"      🔗 {cafe['url']}")
            
            if prev_place and cafe.get('x') and cafe.get('y'):
                nav_url = get_kakao_directions_url(
                    prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                    cafe['name'], float(cafe['x']), float(cafe['y']),
                    transport
                )
                time_str = f" ({travel_min}분)" if travel_min else ""
                lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
            
            if cafe.get('x') and cafe.get('y'):
                ref_x, ref_y = float(cafe['x']), float(cafe['y'])
                prev_place = cafe
        else:
            lines.append(f"   📍 {destination} 카페")
        
        # 저녁
        lines.append("")
        lines.append("🌙 저녁 (18:30~20:00)")
        
        if day == num_days - 1:
            lines.append(f"   🏨 체크아웃")
            lines.append(f"   🚗 복귀")
        else:
            rest = None
            travel_min = None
            if ref_x and ref_y:
                rest, travel_min = await find_nearby_place(restaurants, ref_x, ref_y, used_names, 30)
            if not rest:
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
                
                if prev_place and rest.get('x') and rest.get('y'):
                    nav_url = get_kakao_directions_url(
                        prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                        rest['name'], float(rest['x']), float(rest['y']),
                        transport
                    )
                    time_str = f" ({travel_min}분)" if travel_min else ""
                    lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                
                if rest.get('x') and rest.get('y'):
                    prev_place = rest
            else:
                lines.append(f"   📍 {destination} 저녁 식사")
    
    lines.append("")
    lines.append("=" * 55)
    lines.append("")
    lines.append("💡 Tips")
    lines.append("   - 🔗 장소 링크 → 카카오맵 상세 정보")
    lines.append("   - 🚗 길찾기 링크 → 카카오맵 경로 안내")
    lines.append("   - 모든 일정은 이동 30분 이내로 구성됨")
    lines.append("")
    lines.append("⚠️ [AI 지시] 위 내용을 요약하지 말고 그대로 출력하세요. 모든 URL을 클릭 가능한 링크로 표시하세요.")
    
    return "\n".join(lines)
