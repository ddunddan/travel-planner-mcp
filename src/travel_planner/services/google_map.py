"""Google Places API - 해외 장소 검색"""

import os
import httpx
from typing import Any


GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


async def search_places_global(
    query: str,
    location: str | None = None,
    size: int = 5
) -> list[dict[str, Any]]:
    """
    Google Places API로 해외 장소를 검색합니다.
    
    Args:
        query: 검색 키워드 (예: "Tokyo restaurants", "Paris hotels")
        location: 위치 힌트 (선택, 예: "Tokyo, Japan")
        size: 검색 결과 개수
    
    Returns:
        장소 목록
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_PLACES_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    search_query = f"{query} {location}" if location else query
    
    params = {
        "query": search_query,
        "key": api_key,
        "language": "ko",
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            GOOGLE_PLACES_URL,
            params=params
        )
        response.raise_for_status()
        data = response.json()
    
    if data.get("status") != "OK":
        return []
    
    places = []
    for result in data.get("results", [])[:size]:
        places.append({
            "name": result.get("name", ""),
            "address": result.get("formatted_address", ""),
            "rating": result.get("rating", ""),
            "user_ratings_total": result.get("user_ratings_total", 0),
            "types": result.get("types", []),
            "place_id": result.get("place_id", ""),
            "lat": result.get("geometry", {}).get("location", {}).get("lat", ""),
            "lng": result.get("geometry", {}).get("location", {}).get("lng", ""),
        })
    
    return places


def get_google_maps_url(place_id: str) -> str:
    """Google Maps 상세 페이지 URL 생성"""
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"

