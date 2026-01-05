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
    """스카이스캐너 항공권 검색 URL 생성"""
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
    # 좌석 등급 매핑
    cabin_map = {
        "economy": "Y",
        "premiumeconomy": "PE",
        "business": "C",
        "first": "F"
    }
    
    # 국내선/국제선 구분
    domestic_airports = {"CJU", "GMP", "PUS", "TAE", "KWJ", "RSU", "USN", "MWX", "HIN", "WJU"}
    is_domestic = origin.upper() in domestic_airports and destination.upper() in domestic_airports
    flight_type = "domestic" if is_domestic else "international"
    
    dep_date_formatted = departure_date.replace("-", "")
    
    if return_date:
        ret_date_formatted = return_date.replace("-", "")
        url = f"https://flight.naver.com/flights/{flight_type}/{origin}-{destination}-{dep_date_formatted}/{destination}-{origin}-{ret_date_formatted}"
    else:
        url = f"https://flight.naver.com/flights/{flight_type}/{origin}-{destination}-{dep_date_formatted}"
    
    params = {
        "adult": adults,
        "child": children,
        "infant": infants,
        "fareType": cabin_map.get(cabin_class, "Y"),
    }
    
    return f"{url}?{urlencode(params)}"


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
    base_url = "https://www.google.com/travel/flights"
    
    params = {
        "hl": "ko",
        "curr": "KRW",
    }
    
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
    children: int = 0
) -> str:
    """Booking.com 호텔 검색 URL 생성"""
    params = {
        "ss": destination,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "group_adults": adults,
        "no_rooms": rooms,
        "group_children": children,
    }
    
    return f"https://www.booking.com/searchresults.ko.html?{urlencode(params)}"


def get_expedia_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    children: int = 0
) -> str:
    """Expedia 호텔 검색 URL 생성"""
    params = {
        "destination": destination,
        "startDate": checkin_date,
        "endDate": checkout_date,
        "adults": adults,
        "rooms": rooms,
    }
    
    return f"https://www.expedia.co.kr/Hotel-Search?{urlencode(params)}"


def get_yanolja_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2
) -> str:
    """야놀자 숙박 검색 URL 생성 (국내 전용)"""
    keyword = quote(destination)
    
    params = {
        "keyword": quote(destination),
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
        "adultPax": adults,
    }
    
    return f"https://www.yanolja.com/search/{keyword}?{urlencode(params)}"


def get_yeogi_url(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2
) -> str:
    """여기어때 숙박 검색 URL 생성 (국내 전용)"""
    params = {
        "keyword": destination,
        "checkIn": checkin_date,
        "checkOut": checkout_date,
        "personal": adults,
    }
    
    return f"https://www.yeogi.com/domestic-accommodations?{urlencode(params)}"


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
