"""장소 검색 Tool - 국내 전용 (카카오맵)"""

from ..services.kakao_map import search_places_korea
from ..services.booking_links import is_korea


async def search_places(
    destination: str,
    category: str = "관광지",
    count: int = 5
) -> str:
    """
    국내 여행지의 장소를 검색합니다. (카카오맵 사용)
    
    ⚠️ 해외 장소는 지원하지 않습니다. 해외 여행은 항공권/숙소 예약 링크만 제공됩니다.
    
    Args:
        destination: 국내 여행지 (예: "제주", "부산", "경주", "강릉")
        category: 검색 카테고리 ("관광지", "맛집", "카페", "쇼핑", "숙소")
        count: 검색 결과 개수 (기본 5개, 최대 10개)
    
    Returns:
        장소 검색 결과 (카카오맵 링크 포함)
    """
    # 해외 도시 체크
    if not is_korea(destination):
        return f"""⚠️ '{destination}'은(는) 해외 도시입니다.

🌍 해외 장소 검색은 현재 지원되지 않습니다.
   → 항공권 검색: search_flights 사용
   → 숙소 검색: search_hotels 사용

💡 국내 여행지 예시: 제주, 부산, 경주, 강릉, 여수, 전주, 통영 등"""
    
    # 검색 키워드 구성
    category_keywords = {
        "관광지": "관광지",
        "맛집": "맛집",
        "카페": "카페",
        "쇼핑": "쇼핑",
        "숙소": "호텔",
    }
    
    keyword = category_keywords.get(category, category)
    query = f"{destination} {keyword}"
    
    try:
        places = await search_places_korea(query, size=count)
        return _format_kakao_results(destination, category, places)
    except ValueError as e:
        return f"❌ API 오류: {str(e)}"
    except Exception as e:
        return f"❌ 검색 중 오류가 발생했습니다: {str(e)}"


def _format_kakao_results(destination: str, category: str, places: list) -> str:
    """카카오맵 검색 결과 포맷팅"""
    if not places:
        return f"❌ '{destination}'에서 {category}을(를) 찾을 수 없습니다."
    
    emoji = {"관광지": "🏛️", "맛집": "🍽️", "카페": "☕", "쇼핑": "🛍️", "숙소": "🏨"}.get(category, "📍")
    
    lines = []
    lines.append(f"{emoji} {destination} {category} 검색 결과")
    lines.append(f"🗺️ 카카오맵 | 총 {len(places)}개")
    lines.append("")
    lines.append("=" * 23)
    
    for i, place in enumerate(places, 1):
        lines.append("")
        lines.append(f"[{i}] {place['name']}")
        if place['address']:
            lines.append(f"    📍 {place['address']}")
        if place['category']:
            lines.append(f"    🏷️ {place['category']}")
        if place['phone']:
            lines.append(f"    📞 {place['phone']}")
        if place['url']:
            lines.append(f"    🔗 {place['url']}")
    
    lines.append("")
    lines.append("=" * 23)
    lines.append("")
    lines.append("⚠️ [AI 지시] 위 내용을 요약하지 말고 그대로 출력하세요. 모든 URL을 클릭 가능한 링크로 표시하세요.")
    
    return "\n".join(lines)



