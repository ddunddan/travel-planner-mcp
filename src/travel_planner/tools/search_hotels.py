"""호텔/숙소 검색 Tool - 예약 링크 생성"""

from ..services.booking_links import (
    get_booking_url,
    get_agoda_url,
    get_yanolja_url,
    get_yeogi_url,
    is_korea,
)


async def search_hotels(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0
) -> str:
    """
    숙소 예약 링크를 생성합니다.
    
    - 국내: 야놀자, 여기어때, Booking, Agoda
    - 해외: Booking, Agoda
    
    Args:
        destination: 목적지 (필수, 예: "제주", "강릉", "도쿄")
        checkin_date: 체크인 날짜 (필수, YYYY-MM-DD)
        checkout_date: 체크아웃 날짜 (필수, YYYY-MM-DD)
        adults: 성인 인원 (기본 2명)
        rooms: 객실 수 (기본 1개)
        children: 어린이 수 (기본 0명)
    
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
    lines.append("")
    lines.append("-" * 50)
    lines.append("")
    lines.append("📌 아래 링크를 클릭하여 실시간 가격을 확인하세요!")
    lines.append("")
    
    # 국내 전용 사이트
    if is_domestic:
        # 야놀자
        yanolja_url = get_yanolja_url(destination, checkin_date, checkout_date, adults)
        lines.append("🟣 야놀자")
        lines.append(f"   {yanolja_url}")
        lines.append("")
        
        # 여기어때
        yeogi_url = get_yeogi_url(destination, checkin_date, checkout_date, adults)
        lines.append("🔵 여기어때")
        lines.append(f"   {yeogi_url}")
        lines.append("")
    
    # 글로벌 사이트
    booking_url = get_booking_url(destination, checkin_date, checkout_date, adults, rooms, children)
    lines.append("🟠 Booking.com")
    lines.append(f"   {booking_url}")
    lines.append("")
    
    agoda_url = get_agoda_url(destination, checkin_date, checkout_date, adults, rooms, children)
    lines.append("🔴 Agoda")
    lines.append(f"   {agoda_url}")
    
    lines.append("")
    lines.append("=" * 50)
    lines.append("")
    lines.append("💡 Tip: 여러 사이트를 비교해서 최저가를 찾아보세요!")
    
    return "\n".join(lines)
