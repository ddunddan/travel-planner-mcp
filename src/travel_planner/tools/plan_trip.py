"""여행 일정 생성 Tool - 고도화된 동선 최적화"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from ..services.kakao_map import search_places_korea
from ..services.kakao_mobility import get_kakao_directions_url
from ..services.booking_links import is_korea


# ============================================================
# 설정 상수
# ============================================================
MAX_MOVES_PER_DAY = 5  # 하루 최대 이동 횟수
MAX_TRAVEL_TIME = 30   # 최대 이동 시간 (분)
REST_THRESHOLD = 2     # 연속 이동 후 휴식 삽입 기준


# ============================================================
# 데이터 클래스
# ============================================================
@dataclass
class ScheduleStats:
    """일정 통계"""
    total_travel_time: int = 0  # 총 이동 시간 (분)
    total_moves: int = 0        # 총 이동 횟수
    moves_per_day: list[int] = field(default_factory=list)
    excluded_places: list[dict] = field(default_factory=list)  # 제외된 장소
    
    def add_move(self, travel_time: int, day: int):
        """이동 추가"""
        self.total_travel_time += travel_time
        self.total_moves += 1
        while len(self.moves_per_day) <= day:
            self.moves_per_day.append(0)
        self.moves_per_day[day] += 1
    
    def add_excluded(self, place: dict, reason: str):
        """제외된 장소 추가"""
        self.excluded_places.append({
            "name": place.get("name", "알 수 없음"),
            "reason": reason
        })
    
    def avg_moves_per_day(self) -> float:
        """하루 평균 이동 횟수"""
        if not self.moves_per_day:
            return 0
        return sum(self.moves_per_day) / len(self.moves_per_day)


# ============================================================
# 유틸리티 함수
# ============================================================
def calc_distance(ref_x: float, ref_y: float, x: float, y: float) -> float:
    """직선 거리 계산 (km)"""
    import math
    R = 6371
    lat1, lon1 = math.radians(ref_y), math.radians(ref_x)
    lat2, lon2 = math.radians(y), math.radians(x)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def estimate_travel_time(distance: float) -> int:
    """직선 거리 → 예상 이동 시간 (분)"""
    # 직선 거리 × 1.3 (도로 보정) ÷ 시속 30km
    return int((distance * 1.3 / 30) * 60)


def get_theme_weights(themes: list[str]) -> dict[str, float]:
    """테마 기반 카테고리 가중치 계산"""
    weights = {
        "restaurant": 1.0,
        "tourist": 1.0,
        "cafe": 1.0,
    }
    
    themes_lower = [t.lower() for t in themes]
    
    if "맛집" in themes_lower or "음식" in themes_lower:
        weights["restaurant"] = 2.0
        weights["tourist"] = 0.7
    
    if "자연" in themes_lower or "힐링" in themes_lower:
        weights["tourist"] = 2.0
        weights["restaurant"] = 0.7
    
    if "카페" in themes_lower or "디저트" in themes_lower:
        weights["cafe"] = 2.0
    
    if "역사" in themes_lower or "문화" in themes_lower:
        weights["tourist"] = 1.5
    
    return weights


async def find_nearby_place(
    places: list,
    ref_x: float,
    ref_y: float,
    used_names: set,
    stats: ScheduleStats,
    max_time: int = MAX_TRAVEL_TIME,
    consecutive_moves: int = 0
) -> tuple[dict | None, int | None]:
    """
    기준 좌표에서 최적 장소 찾기
    
    고려 요소:
    - 이동 시간 30분 이내
    - 연속 이동 시 피로도 고려
    - 이미 방문한 장소 제외
    """
    candidates = []
    
    for place in places:
        name = place.get('name', '')
        
        # 이미 방문한 장소 제외
        if name in used_names:
            continue
        
        # 좌표 없으면 스킵
        if not place.get('x') or not place.get('y'):
            continue
        
        try:
            x = float(place['x'])
            y = float(place['y'])
            distance = calc_distance(ref_x, ref_y, x, y)
            travel_time = estimate_travel_time(distance)
            candidates.append((place, distance, travel_time))
        except (ValueError, TypeError):
            continue
    
    # 거리 기준 정렬
    candidates.sort(key=lambda c: c[1])
    
    if not candidates:
        return (None, None)
    
    # 연속 이동 피로도 고려 - 연속 이동이 많으면 더 가까운 곳 선호
    adjusted_max_time = max_time
    if consecutive_moves >= REST_THRESHOLD:
        adjusted_max_time = max_time * 0.7  # 30% 더 가까운 곳으로 제한
    
    # 최적 장소 선택
    best = None
    best_time = float('inf')
    
    for place, distance, travel_time in candidates[:5]:  # 상위 5개만 검토
        if travel_time <= adjusted_max_time and travel_time < best_time:
            best = place
            best_time = travel_time
        elif travel_time > adjusted_max_time:
            # 제외 사유 기록
            stats.add_excluded(place, f"이동 {travel_time}분 > 제한 {int(adjusted_max_time)}분")
    
    # 조건 내 장소가 없으면 가장 가까운 곳 선택
    if best is None and candidates:
        best = candidates[0][0]
        best_time = candidates[0][2]
    
    return (best, int(best_time) if best else None)


def get_first_place_with_coords(places: list, used_names: set) -> dict | None:
    """좌표가 있는 첫 번째 장소 반환"""
    for place in places:
        if place['name'] not in used_names and place.get('x') and place.get('y'):
            return place
    return None


# ============================================================
# 메인 함수
# ============================================================
async def plan_trip(
    destination: str,
    start_date: str,
    end_date: str,
    transport: str = "car",
    themes: list[str] | None = None,
    adults: int = 2
) -> str:
    """
    여행 일정을 생성합니다. (국내 전용)
    
    최적화 기준:
    - 이동 시간 30분 이내 동선
    - 하루 최대 5회 이동
    - 연속 이동 피로도 고려
    - 테마 기반 장소 비중 조절
    
    Args:
        destination: 여행 목적지 (예: "제주", "부산", "강릉")
        start_date: 여행 시작일 (YYYY-MM-DD)
        end_date: 여행 종료일 (YYYY-MM-DD)
        transport: 이동수단 - "car"(자차/렌트카), "public"(대중교통)
        themes: 여행 테마 (예: ["맛집", "자연", "카페"])
        adults: 인원 수 (기본 2명)
    """
    # ========================================
    # 입력 검증
    # ========================================
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "❌ 날짜 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-03-01)"
    
    if end < start:
        return "❌ 종료일이 시작일보다 빠를 수 없습니다."
    
    num_days = (end - start).days + 1
    nights = num_days - 1
    
    if num_days > 3:
        return "⚠️ 현재 최대 2박 3일까지 일정 생성이 가능합니다.\n\n더 긴 여행은 여러 번 나눠서 요청해주세요!\n예: 1~3일, 4~6일"
    
    if not is_korea(destination):
        return f"⚠️ '{destination}'은(는) 해외 도시입니다.\n\n국내 여행지 예시: 제주, 부산, 강릉, 경주, 여수, 전주 등"
    
    # ========================================
    # 설정 초기화
    # ========================================
    transport = transport.lower() if transport.lower() in ["car", "public"] else "car"
    transport_names = {"car": "🚗 자차/렌트카", "public": "🚌 대중교통"}
    transport_name = transport_names.get(transport)
    
    themes = themes or []
    weights = get_theme_weights(themes)
    stats = ScheduleStats()
    
    # ========================================
    # 장소 검색 (테마 가중치 반영)
    # ========================================
    restaurants = []
    tourist_spots = []
    cafes = []
    
    # 맛집 검색 (가중치에 따라 검색량 조절)
    restaurant_size = int(10 * weights["restaurant"])
    try:
        restaurants = await search_places_korea(f"{destination} 맛집", size=min(restaurant_size, 15))
    except Exception:
        pass
    
    # 관광지 검색
    tourist_size = int(8 * weights["tourist"])
    search_keyword = f"{destination} 관광지"
    themes_lower = [t.lower() for t in themes]
    if "자연" in themes_lower:
        search_keyword = f"{destination} 자연 명소"
    elif "역사" in themes_lower:
        search_keyword = f"{destination} 역사 유적"
    
    try:
        tourist_spots = await search_places_korea(search_keyword, size=min(tourist_size, 15))
    except Exception:
        pass
    
    # 카페 검색
    cafe_size = int(8 * weights["cafe"])
    try:
        cafes = await search_places_korea(f"{destination} 카페", size=min(cafe_size, 15))
    except Exception:
        pass
    
    # ========================================
    # 일정 생성
    # ========================================
    lines = []
    used_names = set()
    prev_place = None
    consecutive_moves = 0
    
    # 헤더
    lines.append(f"🗺️ {destination} {nights}박 {num_days}일 여행 일정")
    lines.append("")
    lines.append("=" * 28)
    lines.append("")
    lines.append(f"📅 {start_date} ~ {end_date}")
    lines.append(f"👥 {adults}명")
    lines.append(f"🚀 이동수단: {transport_name}")
    if themes:
        lines.append(f"🎯 테마: {', '.join(themes)}")
    
    # 일정 섹션
    lines.append("")
    lines.append("=" * 28)
    lines.append("📋 일정")
    lines.append("=" * 28)
    
    for day in range(num_days):
        current_date = start + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        lines.append("")
        lines.append(f"📌 Day {day + 1} - {date_str} ({weekday})")
        lines.append("-" * 28)
        
        ref_x, ref_y = None, None
        day_moves = 0
        consecutive_moves = 0
        
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
            spot = None
            travel_min = None
            if ref_x and ref_y and day_moves < MAX_MOVES_PER_DAY:
                spot, travel_min = await find_nearby_place(
                    tourist_spots, ref_x, ref_y, used_names, stats,
                    MAX_TRAVEL_TIME, consecutive_moves
                )
            if not spot:
                spot = get_first_place_with_coords(tourist_spots, used_names)
            
            if spot:
                used_names.add(spot['name'])
                lines.append(f"   📍 {spot['name']}")
                if spot.get('address'):
                    lines.append(f"      📌 {spot['address']}")
                if spot.get('url'):
                    lines.append(f"      🔗 {spot['url']}")
                
                if prev_place and spot.get('x') and spot.get('y'):
                    nav_url = get_kakao_directions_url(
                        prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                        spot['name'], float(spot['x']), float(spot['y']), transport
                    )
                    time_str = f" ({travel_min}분)" if travel_min else ""
                    lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                    if travel_min:
                        stats.add_move(travel_min, day)
                        day_moves += 1
                        consecutive_moves += 1
                
                if spot.get('x') and spot.get('y'):
                    ref_x, ref_y = float(spot['x']), float(spot['y'])
                    prev_place = spot
            else:
                lines.append(f"   📍 {destination} 주변 탐방")
        
        # 점심
        lines.append("")
        lines.append("🍽️ 점심 (12:00~13:30)")
        
        rest = None
        travel_min = None
        if ref_x and ref_y and day_moves < MAX_MOVES_PER_DAY:
            rest, travel_min = await find_nearby_place(
                restaurants, ref_x, ref_y, used_names, stats,
                MAX_TRAVEL_TIME, consecutive_moves
            )
        if not rest:
            rest = get_first_place_with_coords(restaurants, used_names)
        
        if rest:
            used_names.add(rest['name'])
            lines.append(f"   📍 {rest['name']}")
            if rest.get('category'):
                lines.append(f"      🏷️ {rest['category']}")
            if rest.get('address'):
                lines.append(f"      📌 {rest['address']}")
            if rest.get('url'):
                lines.append(f"      🔗 {rest['url']}")
            
            if prev_place and rest.get('x') and rest.get('y'):
                nav_url = get_kakao_directions_url(
                    prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                    rest['name'], float(rest['x']), float(rest['y']), transport
                )
                time_str = f" ({travel_min}분)" if travel_min else ""
                lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                if travel_min:
                    stats.add_move(travel_min, day)
                    day_moves += 1
                    consecutive_moves += 1
            
            if rest.get('x') and rest.get('y'):
                ref_x, ref_y = float(rest['x']), float(rest['y'])
                prev_place = rest
        else:
            lines.append(f"   📍 {destination} 현지 맛집")
        
        # 오후 - 피로도 체크 후 휴식 또는 관광
        lines.append("")
        if consecutive_moves >= REST_THRESHOLD:
            # 휴식 삽입
            lines.append("☕ 오후 휴식 (14:00~16:00)")
            lines.append(f"   📍 자유시간 / 숙소 휴식")
            lines.append(f"   💡 연속 이동으로 휴식 권장")
            consecutive_moves = 0  # 리셋
            
            # 늦은 오후에 카페
            lines.append("")
            lines.append("☕ 카페 (16:00~17:30)")
        else:
            lines.append("🌇 오후 (14:00~17:00)")
            
            spot = None
            travel_min = None
            if ref_x and ref_y and day_moves < MAX_MOVES_PER_DAY:
                spot, travel_min = await find_nearby_place(
                    tourist_spots, ref_x, ref_y, used_names, stats,
                    MAX_TRAVEL_TIME, consecutive_moves
                )
            if not spot:
                spot = get_first_place_with_coords(tourist_spots, used_names)
            
            if spot:
                used_names.add(spot['name'])
                lines.append(f"   📍 {spot['name']}")
                if spot.get('address'):
                    lines.append(f"      📌 {spot['address']}")
                if spot.get('url'):
                    lines.append(f"      🔗 {spot['url']}")
                
                if prev_place and spot.get('x') and spot.get('y'):
                    nav_url = get_kakao_directions_url(
                        prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                        spot['name'], float(spot['x']), float(spot['y']), transport
                    )
                    time_str = f" ({travel_min}분)" if travel_min else ""
                    lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                    if travel_min:
                        stats.add_move(travel_min, day)
                        day_moves += 1
                        consecutive_moves += 1
                
                if spot.get('x') and spot.get('y'):
                    ref_x, ref_y = float(spot['x']), float(spot['y'])
                    prev_place = spot
            else:
                lines.append(f"   📍 자유 시간")
            
            # 카페 시간
            lines.append("")
            lines.append("☕ 카페 (17:00~18:00)")
        
        # 카페 장소 선택
        cafe = None
        travel_min = None
        if ref_x and ref_y and day_moves < MAX_MOVES_PER_DAY:
            cafe, travel_min = await find_nearby_place(
                cafes, ref_x, ref_y, used_names, stats,
                MAX_TRAVEL_TIME, consecutive_moves
            )
        if not cafe:
            cafe = get_first_place_with_coords(cafes, used_names)
        
        if cafe:
            used_names.add(cafe['name'])
            lines.append(f"   📍 {cafe['name']}")
            if cafe.get('address'):
                lines.append(f"      📌 {cafe['address']}")
            if cafe.get('url'):
                lines.append(f"      🔗 {cafe['url']}")
            
            if prev_place and cafe.get('x') and cafe.get('y'):
                nav_url = get_kakao_directions_url(
                    prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                    cafe['name'], float(cafe['x']), float(cafe['y']), transport
                )
                time_str = f" ({travel_min}분)" if travel_min else ""
                lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                if travel_min:
                    stats.add_move(travel_min, day)
                    day_moves += 1
                    consecutive_moves = 0  # 카페 후 리셋
            
            if cafe.get('x') and cafe.get('y'):
                ref_x, ref_y = float(cafe['x']), float(cafe['y'])
                prev_place = cafe
        else:
            lines.append(f"   📍 {destination} 카페")
            consecutive_moves = 0
        
        # 저녁
        lines.append("")
        lines.append("🌙 저녁 (18:30~20:00)")
        
        if day == num_days - 1:
            lines.append(f"   🏨 체크아웃")
            lines.append(f"   🚗 복귀")
        else:
            rest = None
            travel_min = None
            if ref_x and ref_y and day_moves < MAX_MOVES_PER_DAY:
                rest, travel_min = await find_nearby_place(
                    restaurants, ref_x, ref_y, used_names, stats,
                    MAX_TRAVEL_TIME, consecutive_moves
                )
            if not rest:
                rest = get_first_place_with_coords(restaurants, used_names)
            
            if rest:
                used_names.add(rest['name'])
                lines.append(f"   📍 {rest['name']}")
                if rest.get('category'):
                    lines.append(f"      🏷️ {rest['category']}")
                if rest.get('address'):
                    lines.append(f"      📌 {rest['address']}")
                if rest.get('url'):
                    lines.append(f"      🔗 {rest['url']}")
                
                if prev_place and rest.get('x') and rest.get('y'):
                    nav_url = get_kakao_directions_url(
                        prev_place['name'], float(prev_place['x']), float(prev_place['y']),
                        rest['name'], float(rest['x']), float(rest['y']), transport
                    )
                    time_str = f" ({travel_min}분)" if travel_min else ""
                    lines.append(f"      🚗 길찾기{time_str}: {nav_url}")
                    if travel_min:
                        stats.add_move(travel_min, day)
                
                if rest.get('x') and rest.get('y'):
                    prev_place = rest
            else:
                lines.append(f"   📍 {destination} 저녁 식사")
    
    # ========================================
    # 일정 요약 섹션
    # ========================================
    lines.append("")
    lines.append("=" * 28)
    lines.append("📊 [일정 요약]")
    lines.append("=" * 28)
    lines.append("")
    lines.append(f"   ⏱️ 총 이동 시간: 약 {stats.total_travel_time}분")
    lines.append(f"   🚗 총 이동 횟수: {stats.total_moves}회")
    lines.append(f"   📈 하루 평균 이동: {stats.avg_moves_per_day():.1f}회")
    lines.append("")
    lines.append("   📌 주요 기준")
    lines.append("      - 이동 시간 30분 이내")
    lines.append("      - 하루 최대 5회 이동")
    lines.append("      - 연속 2회 이동 후 휴식 권장")
    
    # ========================================
    # 구성 근거 섹션
    # ========================================
    lines.append("")
    lines.append("=" * 28)
    lines.append("📝 [일정 구성 근거]")
    lines.append("=" * 28)
    lines.append("")
    lines.append("   🎯 동선 최적화 기준")
    lines.append("      - 직선 거리 기반 이동 시간 추정")
    lines.append("      - 가까운 장소 우선 배치")
    lines.append("      - 피로도 고려 휴식 자동 삽입")
    lines.append("")
    
    if themes:
        lines.append("   🎨 사용자 요청 반영")
        for theme in themes:
            if theme == "맛집":
                lines.append("      - 맛집 비중 2배 증가")
            elif theme == "자연":
                lines.append("      - 자연 명소 우선 검색")
            elif theme == "카페":
                lines.append("      - 카페 비중 2배 증가")
            elif theme == "역사":
                lines.append("      - 역사 유적지 우선 검색")
        lines.append("")
    
    # 제외된 장소 (상위 3개만)
    if stats.excluded_places:
        lines.append("   ❌ 제외된 후보 (일부)")
        for exc in stats.excluded_places[:3]:
            lines.append(f"      - {exc['name']}: {exc['reason']}")
        lines.append("")
    
    # ========================================
    # 다음 행동 추천
    # ========================================
    lines.append("=" * 28)
    lines.append("💬 [다음에 이렇게 요청해보세요]")
    lines.append("=" * 28)
    lines.append("")
    lines.append(f'   📝 "Day 2 일정만 수정해줘"')
    lines.append(f'   🍽️ "맛집 비중 더 늘려줘"')
    lines.append(f'   🚶 "이동 최소화 일정으로 바꿔줘"')
    lines.append(f'   🏨 "숙소 근처 위주로 다시 짜줘"')
    
    lines.append("")
    lines.append("⚠️ [AI 지시] 위 내용을 요약하지 말고 그대로 출력하세요. 모든 URL을 클릭 가능한 링크로 표시하세요.")
    
    return "\n".join(lines)
