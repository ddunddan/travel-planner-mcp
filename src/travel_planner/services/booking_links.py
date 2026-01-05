"""예약 링크 생성 서비스 - API 키 불필요"""

from urllib.parse import quote, urlencode
from datetime import datetime


# ============================================================
# 항공권 예약 링크 생성
# ============================================================

def get_skyscanner_flight_url(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin_class: str = "economy",
    direct_only: bool = False
) -> str:
    """
    스카이스캐너 항공권 검색 URL 생성
    
    Args:
        origin: 출발 공항 IATA 코드
        destination: 도착 공항 IATA 코드
        departure_date: 출발일 YYYY-MM-DD
        return_date: 귀국일 (편도면 None)
        adults: 성인 인원
        children: 어린이 인원 (2-11세)
        infants: 유아 인원 (0-2세)
        cabin_class: 좌석 등급 (economy, premiumeconomy, business, first)
        direct_only: 직항만 검색
    """
    # 날짜 형식 변환: YYYY-MM-DD -> YYMMDD
    dep_date = departure_date.replace("-", "")[2:]
    
    if return_date:
        ret_date = return_date.replace("-", "")[2:]
        url = f"https://www.skyscanner.co.kr/transport/flights/{origin.lower()}/{destination.lower()}/{dep_date}/{ret_date}/"
    else:
        url = f"https://www.skyscanner.co.kr/transport/flights/{origin.lower()}/{destination.lower()}/{dep_date}/"
    
    params = {
        "adults": adults,
        "adultsv2": adults,
        "cabinclass": cabin_class,
        "children": children,
        "childrenv2": "",
        "infants": infants,
        "rtn": 1 if return_date else 0,
    }
    
    if direct_only:
        params["preferdirects"] = "true"
    
    return f"{url}?{urlencode(params)}"


def get_naver_flight_url(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin_class: str = "economy"
) -> str:
    """네이버 항공권 검색 URL 생성"""
    trip_type = "RT" if return_date else "OW"
    
    # 좌석 등급 매핑
    cabin_map = {
        "economy": "Y",
        "premiumeconomy": "PE",
        "business": "C",
        "first": "F"
    }
    
    params = {
        "trip": trip_type,
        "scity1": origin,
        "ecity1": destination,
        "sdate1": departure_date,
        "adult": adults,
        "child": children,
        "infant": infants,
        "cabin": cabin_map.get(cabin_class, "Y"),
    }
    
    if return_date:
        params["sdate2"] = return_date
    
    return f"https://flight.naver.com/flights/international/{origin}-{destination}-{departure_date.replace('-', '')}?{urlencode(params)}"


def get_google_flights_url(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    cabin_class: str = "economy",
    direct_only: bool = False
) -> str:
    """구글 플라이트 검색 URL 생성"""
    # 좌석 등급 매핑
    cabin_map = {
        "economy": "1",
        "premiumeconomy": "2", 
        "business": "3",
        "first": "4"
    }
    
    base_url = "https://www.google.com/travel/flights"
    
    params = {
        "hl": "ko",
        "curr": "KRW",
    }
    
    # 구글 플라이트 URL 형식
    if return_date:
        flight_path = f"/search?q=flights+from+{origin}+to+{destination}+on+{departure_date}+return+{return_date}"
    else:
        flight_path = f"/search?q=flights+from+{origin}+to+{destination}+on+{departure_date}+oneway"
    
    return f"{base_url}{flight_path}&{urlencode(params)}"


# ============================================================
# 호텔 예약 링크 생성
# ============================================================

def get_booking_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0,
    sort_by: str = "popularity",
    min_rating: int | None = None,
    breakfast_included: bool = False,
    free_cancellation: bool = False
) -> str:
    """
    Booking.com 호텔 검색 URL 생성
    
    Args:
        destination: 목적지
        checkin_date: 체크인 YYYY-MM-DD
        checkout_date: 체크아웃 YYYY-MM-DD
        adults: 성인 인원
        rooms: 객실 수
        children: 어린이 수
        sort_by: 정렬 (popularity, price, review_score, distance)
        min_rating: 최소 평점 (6, 7, 8, 9)
        breakfast_included: 조식 포함
        free_cancellation: 무료 취소 가능
    """
    params = {
        "ss": destination,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "group_adults": adults,
        "no_rooms": rooms,
        "group_children": children,
    }
    
    # 정렬
    sort_map = {
        "popularity": "popularity",
        "price": "price",
        "rating": "bayesian_review_score",
        "distance": "distance",
    }
    if sort_by in sort_map:
        params["order"] = sort_map[sort_by]
    
    # 필터
    filters = []
    if min_rating:
        filters.append(f"review_score={min_rating}0")
    if breakfast_included:
        filters.append("mealplan=1")
    if free_cancellation:
        filters.append("fc=2")
    
    if filters:
        params["nflt"] = ";".join(filters)
    
    return f"https://www.booking.com/searchresults.ko.html?{urlencode(params)}"


def get_agoda_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0,
    sort_by: str = "popularity"
) -> str:
    """Agoda 호텔 검색 URL 생성"""
    params = {
        "textToSearch": destination,
        "checkIn": checkin_date,
        "checkOut": checkout_date,
        "rooms": rooms,
        "adults": adults,
        "children": children,
    }
    
    # 정렬
    sort_map = {
        "popularity": "1",
        "price": "2",
        "rating": "5",
        "distance": "4",
    }
    if sort_by in sort_map:
        params["sort"] = sort_map[sort_by]
    
    return f"https://www.agoda.com/search?{urlencode(params)}"


def get_hotels_com_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0,
    sort_by: str = "popularity"
) -> str:
    """Hotels.com 호텔 검색 URL 생성"""
    params = {
        "q-destination": destination,
        "q-check-in": checkin_date,
        "q-check-out": checkout_date,
        "q-rooms": rooms,
        "q-room-0-adults": adults,
        "q-room-0-children": children,
    }
    
    # 정렬
    sort_map = {
        "popularity": "RECOMMENDED",
        "price": "PRICE_LOW_TO_HIGH",
        "rating": "GUEST_RATING",
        "distance": "DISTANCE",
    }
    if sort_by in sort_map:
        params["sort-order"] = sort_map[sort_by]
    
    return f"https://kr.hotels.com/search.do?{urlencode(params)}"


def get_yanolja_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    sort_by: str = "popularity"
) -> str:
    """야놀자 숙박 검색 URL 생성 (국내 전용)"""
    keyword = quote(destination)
    
    params = {
        "keyword": keyword,
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
        "adultPax": adults,
    }
    
    # 정렬
    sort_map = {
        "popularity": "RECOMMEND",
        "price": "PRICE_ASC",
        "rating": "REVIEW_DESC",
    }
    if sort_by in sort_map:
        params["sortType"] = sort_map[sort_by]
    
    return f"https://www.yanolja.com/search/{keyword}?{urlencode(params)}"


def get_goodchoice_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    sort_by: str = "popularity"
) -> str:
    """여기어때 숙박 검색 URL 생성 (국내 전용)"""
    keyword = quote(destination)
    checkin = checkin_date.replace("-", "")
    checkout = checkout_date.replace("-", "")
    
    params = {
        "keyword": keyword,
        "sel_date": checkin,
        "sel_date2": checkout,
    }
    
    # 정렬
    sort_map = {
        "popularity": "1",
        "price": "2",
        "rating": "3",
    }
    if sort_by in sort_map:
        params["order"] = sort_map[sort_by]
    
    return f"https://www.goodchoice.kr/product/search?{urlencode(params)}"


def get_naver_hotel_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0
) -> str:
    """네이버 호텔 검색 URL 생성"""
    keyword = quote(destination)
    
    params = {
        "destination": keyword,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "rooms": rooms,
        "adults": adults,
        "children": children,
    }
    
    return f"https://hotels.naver.com/search?{urlencode(params)}"


# ============================================================
# 공항 코드 매핑
# ============================================================

AIRPORT_CODES = {
    # 한국
    "인천": "ICN", "김포": "GMP", "제주": "CJU", "부산": "PUS", "김해": "PUS",
    "대구": "TAE", "청주": "CJJ", "광주": "KWJ", "여수": "RSU",
    # 일본
    "도쿄": "NRT", "나리타": "NRT", "하네다": "HND", "오사카": "KIX", "간사이": "KIX",
    "후쿠오카": "FUK", "삿포로": "CTS", "오키나와": "OKA", "나하": "OKA",
    # 중국
    "베이징": "PEK", "상하이": "PVG", "홍콩": "HKG", "광저우": "CAN",
    # 동남아
    "방콕": "BKK", "싱가포르": "SIN", "발리": "DPS", "다낭": "DAD",
    "하노이": "HAN", "호치민": "SGN", "세부": "CEB", "마닐라": "MNL",
    "쿠알라룸푸르": "KUL", "푸켓": "HKT", "치앙마이": "CNX",
    # 미주
    "뉴욕": "JFK", "LA": "LAX", "로스앤젤레스": "LAX", "샌프란시스코": "SFO",
    "시애틀": "SEA", "하와이": "HNL", "호놀룰루": "HNL", "괌": "GUM",
    # 유럽
    "파리": "CDG", "런던": "LHR", "로마": "FCO", "바르셀로나": "BCN",
    "암스테르담": "AMS", "프랑크푸르트": "FRA", "뮌헨": "MUC",
    # 오세아니아
    "시드니": "SYD", "멜버른": "MEL", "오클랜드": "AKL",
}


def get_airport_code(city: str) -> str:
    """도시명으로 공항 코드 반환"""
    if len(city) == 3 and city.isupper():
        return city
    
    for name, code in AIRPORT_CODES.items():
        if name in city:
            return code
    
    return city.upper()[:3]


# 한국 도시 목록
KOREA_CITIES = {
    "서울", "인천", "부산", "대구", "광주", "대전", "울산", "세종",
    "제주", "경주", "강릉", "속초", "전주", "여수", "통영", "거제",
    "춘천", "안동", "포항", "목포", "순천", "군산",
}


def is_korea(city: str) -> bool:
    """국내 도시인지 판단"""
    for korea_city in KOREA_CITIES:
        if korea_city in city:
            return True
    return False
