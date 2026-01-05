"""Travel Planner MCP Server 테스트 스크립트"""

import asyncio
import os

# 테스트용 API 키 설정 (실제 키로 교체)
# os.environ["KAKAO_REST_API_KEY"] = "your_kakao_api_key"
# os.environ["GOOGLE_PLACES_API_KEY"] = "your_google_api_key"  # 해외용, 선택

from src.travel_planner.tools.search_places import search_places
from src.travel_planner.tools.search_flights import search_flights
from src.travel_planner.tools.search_hotels import search_hotels
from src.travel_planner.tools.plan_trip import plan_trip


async def test_search_places_korea():
    """국내 장소 검색 테스트 (카카오맵)"""
    print("\n" + "=" * 55)
    print("🏛️ 테스트: 국내 관광지 검색 (제주)")
    print("=" * 55)
    
    result = await search_places("제주", "관광지", 3)
    print(result)


async def test_search_places_food():
    """맛집 검색 테스트"""
    print("\n" + "=" * 55)
    print("🍽️ 테스트: 맛집 검색 (부산)")
    print("=" * 55)
    
    result = await search_places("부산", "맛집", 3)
    print(result)


async def test_search_flights():
    """항공권 검색 테스트 (예약 링크)"""
    print("\n" + "=" * 55)
    print("✈️ 테스트: 항공권 검색 (인천 → 도쿄)")
    print("=" * 55)
    
    result = await search_flights("인천", "도쿄", "2024-05-01", "2024-05-05", 2)
    print(result)


async def test_search_flights_domestic():
    """국내선 항공권 테스트"""
    print("\n" + "=" * 55)
    print("✈️ 테스트: 국내 항공권 검색 (김포 → 제주)")
    print("=" * 55)
    
    result = await search_flights("김포", "제주", "2024-06-01")
    print(result)


async def test_search_hotels_korea():
    """국내 숙소 검색 테스트"""
    print("\n" + "=" * 55)
    print("🏨 테스트: 국내 숙소 검색 (강릉)")
    print("=" * 55)
    
    result = await search_hotels("강릉", "2024-05-01", "2024-05-03", 2, 1)
    print(result)


async def test_search_hotels_overseas():
    """해외 숙소 검색 테스트"""
    print("\n" + "=" * 55)
    print("🏨 테스트: 해외 숙소 검색 (도쿄)")
    print("=" * 55)
    
    result = await search_hotels("도쿄", "2024-05-01", "2024-05-05", 2, 1)
    print(result)


async def test_plan_trip_korea():
    """국내 여행 일정 생성 테스트"""
    print("\n" + "=" * 55)
    print("🗺️ 테스트: 국내 여행 일정 (제주 2박3일)")
    print("=" * 55)
    
    result = await plan_trip("제주", "2024-05-01", "2024-05-03", "서울", 2)
    print(result)


async def test_plan_trip_overseas():
    """해외 여행 일정 생성 테스트"""
    print("\n" + "=" * 55)
    print("🗺️ 테스트: 해외 여행 일정 (도쿄 3박4일)")
    print("=" * 55)
    
    result = await plan_trip("도쿄", "2024-06-01", "2024-06-04", "인천", 2)
    print(result)


async def main():
    """테스트 실행"""
    print("=" * 55)
    print("🧪 Travel Planner MCP Server 테스트")
    print("=" * 55)
    
    # 환경 변수 확인
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    google_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    print(f"\n📋 환경 변수 상태:")
    print(f"   KAKAO_REST_API_KEY: {'✅ 설정됨' if kakao_key else '❌ 미설정'}")
    print(f"   GOOGLE_PLACES_API_KEY: {'✅ 설정됨' if google_key else '⚪ 미설정 (해외용, 선택)'}")
    
    if not kakao_key:
        print("\n⚠️  KAKAO_REST_API_KEY가 없습니다.")
        print("   카카오 개발자 사이트에서 발급:")
        print("   https://developers.kakao.com/")
        print("\n   설정 방법:")
        print("   export KAKAO_REST_API_KEY=your_api_key")
    
    print("\n" + "=" * 55)
    print("📌 예약 링크 테스트 (API 키 불필요)")
    print("=" * 55)
    
    # 예약 링크는 API 키 없이 테스트 가능
    await test_search_flights()
    await test_search_flights_domestic()
    await test_search_hotels_korea()
    await test_search_hotels_overseas()
    
    if kakao_key:
        print("\n" + "=" * 55)
        print("📌 장소 검색 테스트 (카카오맵)")
        print("=" * 55)
        
        await test_search_places_korea()
        await test_search_places_food()
        await test_plan_trip_korea()
    
    print("\n" + "=" * 55)
    print("✅ 테스트 완료!")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
