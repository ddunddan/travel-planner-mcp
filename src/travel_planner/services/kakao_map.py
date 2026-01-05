"""카카오맵 로컬 API - 국내 장소 검색"""

import os
import httpx
from typing import Any


KAKAO_LOCAL_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


async def search_places_korea(
    query: str,
    category: str | None = None,
    size: int = 5
) -> list[dict[str, Any]]:
    """
    카카오 로컬 API로 국내 장소를 검색합니다.
    
    Args:
        query: 검색 키워드 (예: "제주 맛집", "부산 호텔")
        category: 카테고리 필터 (선택)
        size: 검색 결과 개수
    
    Returns:
        장소 목록
    """
    api_key = os.getenv("KAKAO_REST_API_KEY")
    if not api_key:
        raise ValueError("KAKAO_REST_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    
    params = {
        "query": query,
        "size": min(size, 15)
    }
    
    if category:
        params["category_group_code"] = category
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            KAKAO_LOCAL_URL,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
    
    places = []
    for doc in data.get("documents", []):
        places.append({
            "name": doc.get("place_name", ""),
            "address": doc.get("road_address_name") or doc.get("address_name", ""),
            "category": doc.get("category_name", ""),
            "phone": doc.get("phone", ""),
            "url": doc.get("place_url", ""),
            "x": doc.get("x", ""),
            "y": doc.get("y", ""),
        })
    
    return places


# 카카오 카테고리 코드
KAKAO_CATEGORIES = {
    "관광지": "AT4",
    "숙박": "AD5",
    "음식점": "FD6",
    "카페": "CE7",
}

