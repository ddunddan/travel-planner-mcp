"""호텔/숙소 검색 Tool - 예약 링크 생성"""

from ..services.booking_links import get_yanolja_url, is_korea


async def search_hotels(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0,
    sort_by: str = "popularity"
) -> str:
    """
    숙소 예약 링크를 생성합니다. (국내: 야놀자)
    
    ⚠️ 현재 국내 숙소만 지원합니다.
    
    Args:
        destination: 목적지 (필수, 예: "제주", "강릉", "부산")
        checkin_date: 체크인 날짜 (필수, YYYY-MM-DD)
        checkout_date: 체크아웃 날짜 (필수, YYYY-MM-DD)
        adults: 성인 인원 (기본 2명)
        rooms: 객실 수 (기본 1개)
        children: 어린이 수 (기본 0명)
        sort_by: 정렬 기준 - "popularity"(인기순), "price"(가격순) (기본: popularity)
    
    Returns:
        숙소 예약 사이트 링크
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
    
    if not is_domestic:
        return f"""⚠️ '{destination}'은(는) 해외 도시입니다.

🌍 현재 해외 숙소 검색은 지원되지 않습니다.
   → 직접 Booking.com, Agoda 등에서 검색해주세요.

💡 국내 여행지 예시: 제주, 부산, 강릉, 경주, 여수, 전주 등"""
    
    # 정렬 기준 한글
    sort_names = {
        "popularity": "인기순",
        "price": "가격 낮은순",
    }
    sort_name = sort_names.get(sort_by, "인기순")
    
    # 인원 정보
    pax_info = f"성인 {adults}명"
    if children > 0:
        pax_info += f", 어린이 {children}명"
    
    lines = []
    lines.append("🏨 숙소 검색")
    lines.append("")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"📍 {destination}")
    lines.append(f"📅 {checkin_date} ~ {checkout_date} ({nights}박)")
    lines.append(f"👥 {pax_info} | 객실 {rooms}개")
    lines.append(f"📊 정렬: {sort_name}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("")
    lines.append("📌 아래 링크를 클릭하여 실시간 가격을 확인하세요!")
    lines.append("")
    
    # 야놀자
    yanolja_url = get_yanolja_url(destination, checkin_date, checkout_date, adults, sort_by)
    lines.append("🟣 야놀자")
    lines.append(f"   {yanolja_url}")
    lines.append("")
    
    lines.append("=" * 50)
    lines.append("")
    lines.append("💡 Tip: 야놀자에서 호텔, 펜션, 게스트하우스 등 다양한 숙소를 찾을 수 있어요!")
    
    return "\n".join(lines)
