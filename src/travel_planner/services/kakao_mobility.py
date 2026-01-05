"""카카오모빌리티 길찾기 API - 실제 소요 시간 계산"""

import os
import httpx
from urllib.parse import quote


KAKAO_NAVI_URL = "https://apis-navi.kakaomobility.com/v1/directions"


async def get_travel_time(
    origin_x: float,
    origin_y: float,
    dest_x: float,
    dest_y: float
) -> int | None:
    """
    두 좌표 간 자동차 이동 시간 계산 (분)
    
    카카오모빌리티 길찾기 API 사용
    https://developers.kakaomobility.com/docs/navi-api/directions/
    
    Args:
        origin_x: 출발지 X좌표 (경도)
        origin_y: 출발지 Y좌표 (위도)
        dest_x: 목적지 X좌표 (경도)
        dest_y: 목적지 Y좌표 (위도)
    
    Returns:
        이동 시간 (분), 실패 시 None
    """
    api_key = os.getenv("KAKAO_REST_API_KEY")
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    
    params = {
        "origin": f"{origin_x},{origin_y}",
        "destination": f"{dest_x},{dest_y}",
        "summary": "true",  # 요약 정보만
        "priority": "RECOMMEND",  # 추천 경로
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                KAKAO_NAVI_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        # 응답에서 소요 시간 추출 (초 → 분)
        routes = data.get("routes", [])
        if routes and routes[0].get("result_code") == 0:
            duration_sec = routes[0].get("summary", {}).get("duration", 0)
            return duration_sec // 60  # 분 단위로 변환
        
        return None
    
    except Exception:
        return None


def get_kakao_directions_url(
    origin_name: str,
    origin_x: float,
    origin_y: float,
    dest_name: str,
    dest_x: float,
    dest_y: float,
    transport: str = "car"
) -> str:
    """
    카카오맵 길찾기 URL 생성
    
    Args:
        origin_name: 출발지 이름
        origin_x: 출발지 X좌표
        origin_y: 출발지 Y좌표
        dest_name: 목적지 이름
        dest_x: 목적지 X좌표
        dest_y: 목적지 Y좌표
        transport: 이동수단 (car, traffic, walk, bicycle)
    
    Returns:
        카카오맵 길찾기 URL
    """
    # 이동수단 매핑
    transport_map = {
        "car": "car",
        "public": "traffic",
        "walk": "walk",
        "bicycle": "bicycle"
    }
    mode = transport_map.get(transport, "car")
    
    # URL 인코딩
    origin_encoded = quote(origin_name)
    dest_encoded = quote(dest_name)
    
    return f"https://map.kakao.com/link/by/{mode}/{origin_encoded},{origin_y},{origin_x}/{dest_encoded},{dest_y},{dest_x}"

