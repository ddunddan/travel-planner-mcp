"""호텔/숙소 검색 Tool - 예약 링크 생성"""

from ..services.booking_links import (
    get_booking_url,
    get_agoda_url,
    get_hotels_com_url,
    get_yanolja_url,
    get_goodchoice_url,
    is_korea,
)

# 지원하는 숙소 사이트 목록
HOTEL_SITES_DOMESTIC = {
    "booking": {"name": "Booking.com", "emoji": "🟦"},
    "agoda": {"name": "Agoda", "emoji": "🟥"},
    "yanolja": {"name": "야놀자", "emoji": "🟣"},
    "goodchoice": {"name": "여기어때", "emoji": "🔴"},
}

HOTEL_SITES_INTERNATIONAL = {
    "booking": {"name": "Booking.com", "emoji": "🟦"},
    "agoda": {"name": "Agoda", "emoji": "🟥"},
    "hotels": {"name": "Hotels.com", "emoji": "🟨"},
}


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
    호텔/숙소 예약 링크를 생성합니다.
    
    국내: Booking, Agoda, 야놀자, 여기어때
    해외: Booking.com, Agoda, Hotels.com
    
    Args:
        destination: 목적지 (필수, 예: "제주", "강릉", "도쿄", "파리")
        checkin_date: 체크인 날짜 (필수, YYYY-MM-DD)
        checkout_date: 체크아웃 날짜 (필수, YYYY-MM-DD)
        adults: 성인 인원 (기본 2명)
        rooms: 객실 수 (기본 1개)
        children: 어린이 수 (기본 0명)
        sort_by: 정렬 기준 - "popularity", "price", "rating", "distance" (기본: popularity)
        breakfast_included: 조식 포함 숙소만 (기본 False)
        free_cancellation: 무료 취소 가능 숙소만 (기본 False)
        count: 보여줄 사이트 개수 (기본 4개)
        site: 특정 사이트만 보기 ("booking", "agoda", "hotels", "yanolja", "goodchoice" 중 선택)
    
    Returns:
        숙소 예약 사이트별 검색 링크
    """
    # 필수 파라미터 검증
    if not destination:
        return "❌ 목적지(destination)를 입력해주세요.\n예: search_hotels(destination=\"제주\", checkin_date=\"2026-02-01\", checkout_date=\"2026-02-03\")"
    
    if not checkin_date or not checkout_date:
        return "❌ 체크인/체크아웃 날짜를 입력해주세요.\n형식: YYYY-MM-DD"
    
    # 날짜 형식 검증
    from datetime import datetime
    try:
        checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
        checkout = datetime.strptime(checkout_date, "%Y-%m-%d")
        nights = (checkout - checkin).days
    except ValueError:
        return "❌ 날짜 형식이 올바르지 않습니다.\n형식: YYYY-MM-DD (예: 2026-02-01)"
    
    if nights <= 0:
        return "❌ 체크아웃 날짜는 체크인 날짜보다 뒤여야 합니다."
    
    is_domestic = is_korea(destination)
    
    # 정렬 기준 한글
    sort_names = {
        "popularity": "인기순",
        "price": "가격 낮은순",
        "rating": "평점 높은순",
        "distance": "거리순"
    }
    sort_name = sort_names.get(sort_by, "인기순")
    
    # 인원 정보
    pax_info = f"성인 {adults}명"
    if children > 0:
        pax_info += f", 어린이 {children}명"
    
    # 필터 정보
    filters = []
    if breakfast_included:
        filters.append("조식 포함")
    if free_cancellation:
        filters.append("무료 취소")
    
    lines = []
    lines.append("🏨 숙소 검색")
    lines.append("")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"📍 {destination}")
    lines.append(f"📅 {checkin_date} ~ {checkout_date} ({nights}박)")
    lines.append(f"👥 {pax_info} | 객실 {rooms}개")
    lines.append(f"📊 정렬: {sort_name}")
    if filters:
        lines.append(f"🔍 필터: {', '.join(filters)}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("")
    lines.append("📌 아래 링크를 클릭하여 실시간 가격을 확인하세요!")
    lines.append("")
    
    # 특정 사이트만 요청한 경우
    if site:
        site = site.lower()
        url = _get_site_url(site, destination, checkin_date, checkout_date, adults, rooms, children, sort_by, breakfast_included, free_cancellation, is_domestic)
        if url.startswith("❌"):
            return url
        
        site_info = HOTEL_SITES_DOMESTIC.get(site) or HOTEL_SITES_INTERNATIONAL.get(site)
        if site_info:
            lines.append(f"{site_info['emoji']} {site_info['name']}")
            lines.append(f"   {url}")
    else:
        sites_shown = 0
        
        if is_domestic:
            lines.append("🇰🇷 국내 숙소 예약")
            lines.append("")
            
            # 국내: Booking > Agoda > 야놀자 > 여기어때
            for site_key in ["booking", "agoda", "yanolja", "goodchoice"]:
                if sites_shown >= count:
                    break
                url = _get_site_url(site_key, destination, checkin_date, checkout_date, adults, rooms, children, sort_by, breakfast_included, free_cancellation, is_domestic)
                site_info = HOTEL_SITES_DOMESTIC[site_key]
                lines.append(f"{site_info['emoji']} {site_info['name']}")
                lines.append(f"   {url}")
                lines.append("")
                sites_shown += 1
        else:
            lines.append("🌍 해외 숙소 예약")
            lines.append("")
            
            # 해외: Booking > Agoda > Hotels.com
            for site_key in ["booking", "agoda", "hotels"]:
                if sites_shown >= count:
                    break
                url = _get_site_url(site_key, destination, checkin_date, checkout_date, adults, rooms, children, sort_by, breakfast_included, free_cancellation, is_domestic)
                site_info = HOTEL_SITES_INTERNATIONAL[site_key]
                lines.append(f"{site_info['emoji']} {site_info['name']}")
                lines.append(f"   {url}")
                lines.append("")
                sites_shown += 1
    
    lines.append("=" * 50)
    lines.append("")
    lines.append("💡 Tip: 각 사이트마다 할인 이벤트가 다르니 비교해보세요!")
    if is_domestic:
        lines.append("💡 야놀자/여기어때는 펜션, 게스트하우스도 많아요!")
    
    return "\n".join(lines)


def _get_site_url(
    site: str,
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int,
    rooms: int,
    children: int,
    sort_by: str,
    breakfast_included: bool,
    free_cancellation: bool,
    is_domestic: bool
) -> str:
    """사이트별 URL 생성"""
    site = site.lower()
    
    if site == "booking":
        return get_booking_url(
            destination, checkin_date, checkout_date, adults, rooms, children,
            sort_by, None, breakfast_included, free_cancellation
        )
    elif site == "agoda":
        return get_agoda_url(destination, checkin_date, checkout_date, adults, rooms, children, sort_by)
    elif site == "hotels":
        if is_domestic:
            return "❌ Hotels.com은 해외 숙소만 지원합니다."
        return get_hotels_com_url(destination, checkin_date, checkout_date, adults, rooms, children, sort_by)
    elif site == "yanolja":
        if not is_domestic:
            return "❌ 야놀자는 국내 숙소만 지원합니다."
        return get_yanolja_url(destination, checkin_date, checkout_date, adults, sort_by)
    elif site == "goodchoice":
        if not is_domestic:
            return "❌ 여기어때는 국내 숙소만 지원합니다."
        return get_goodchoice_url(destination, checkin_date, checkout_date, adults, sort_by)
    else:
        all_sites = set(HOTEL_SITES_DOMESTIC.keys()) | set(HOTEL_SITES_INTERNATIONAL.keys())
        return f"❌ 지원하지 않는 사이트입니다.\n지원 사이트: {', '.join(all_sites)}"
