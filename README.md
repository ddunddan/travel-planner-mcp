# 🗺️ Travel Planner MCP Server

> **여행 준비, 한 번에 끝!**  
> 항공권 + 숙소 예약 링크부터 맛집/관광지 추천까지 - AI가 여행 일정을 완벽하게 짜드립니다 ✈️🏨🍽️

---

## 📌 MCP 정보

| 항목 | 내용 |
|------|------|
| **식별자** | `travel-planner` |
| **버전** | `1.0.0` |
| **카테고리** | 여행/라이프스타일 |

---

## ✨ 핵심 기능

| 기능 | 설명 |
|------|------|
| ✈️ **항공권 예약** | 스카이스캐너, 네이버항공권 링크 즉시 생성 |
| 🏨 **숙소 예약** | Booking, Agoda, 야놀자, 여기어때 링크 |
| 📍 **장소 검색** | 카카오맵 기반 관광지/맛집/카페 추천 (국내) |
| 🗺️ **일정 생성** | 자차/대중교통/항공 이동수단별 맞춤 일정 |
| 💬 **카카오톡 전송** | 완성된 일정을 나에게 카카오톡으로 전송 |

---

## 🎯 이런 분께 추천!

- "항공권이랑 호텔 비교하려면 사이트 여러개 돌아다녀야 해서 귀찮아..."
- "여행 일정 짜는 게 제일 힘들어..."
- "이번 주말 강릉 당일치기 가려는데 뭐 먹지?"
- "도쿄 2박3일 예약 링크 한번에 받고 싶어!"

---

## 🚀 사용 예시

### 예시 1: 해외 여행 (항공권 + 숙소)
> **"도쿄 2박3일 여행 예약 링크 알려줘"**

```
✈️ 항공권: 스카이스캐너, 네이버항공권 링크
🏨 숙소: Booking.com, Agoda, Hotels.com 링크
```

**사용 Tool:** `search_flights` + `search_hotels`

---

### 예시 2: 국내 여행 (숙소 + 맛집)
> **"이번 주말 강릉 숙소랑 맛집 추천해줘"**

```
🏨 숙소: 야놀자, 여기어때, Booking 링크
🍽️ 맛집: 카카오맵 기반 강릉 맛집 5곳
```

**사용 Tool:** `search_hotels` + `search_places`

---

### 예시 3: 종합 일정 생성 (자차 여행)
> **"서울에서 출발해서 경주 2박3일 자차 여행 일정 짜줘"**

```
🚗 자차 이동: 네이버/카카오 길찾기 링크
🏨 숙소: 주차 가능 숙소 추천 + 예약 링크
📋 일정: Day별 관광지/맛집/카페 (주차장 정보 포함)
```

**사용 Tool:** `plan_trip`

---

## 🛠️ Tool 목록

### 1. `search_flights` - 항공권 예약 링크

| 파라미터 | 필수 | 기본값 | 설명 |
|:---------|:----:|:------:|:-----|
| `destination` | ✅ | - | 목적지 (제주, 도쿄 등) |
| `departure_date` | ✅ | - | 출발일 (YYYY-MM-DD) |
| `origin` | ❌ | 인천 | 출발지 |
| `return_date` | ❌ | - | 귀국일 (편도면 생략) |
| `adults` | ❌ | 1 | 성인 인원 |
| `children` | ❌ | 0 | 어린이 인원 |
| `cabin_class` | ❌ | economy | economy/business/first |
| `direct_only` | ❌ | True | 직항만 |
| `count` | ❌ | 2 | 사이트 개수 |
| `site` | ❌ | - | 특정 사이트만 (skyscanner/naver/google) |

---

### 2. `search_hotels` - 숙소 예약 링크

| 파라미터 | 필수 | 기본값 | 설명 |
|:---------|:----:|:------:|:-----|
| `destination` | ✅ | - | 목적지 |
| `checkin_date` | ✅ | - | 체크인 (YYYY-MM-DD) |
| `checkout_date` | ✅ | - | 체크아웃 (YYYY-MM-DD) |
| `adults` | ❌ | 2 | 성인 인원 |
| `rooms` | ❌ | 1 | 객실 수 |
| `children` | ❌ | 0 | 어린이 수 |
| `sort_by` | ❌ | popularity | popularity/price/rating/distance |
| `count` | ❌ | 4 | 사이트 개수 |
| `site` | ❌ | - | 특정 사이트만 (booking/agoda/yanolja 등) |

**국내:** Booking, Agoda, 야놀자, 여기어때  
**해외:** Booking, Agoda, Hotels.com

---

### 3. `search_places` - 장소 검색 (국내 전용)

| 파라미터 | 필수 | 기본값 | 설명 |
|:---------|:----:|:------:|:-----|
| `destination` | ✅ | - | 국내 지역 (구체적 가능: "서울 홍대") |
| `category` | ❌ | 관광지 | 관광지/맛집/카페/쇼핑/숙소 |
| `count` | ❌ | 5 | 검색 개수 (최대 10) |

---

### 4. `plan_trip` - 종합 여행 일정

| 파라미터 | 필수 | 기본값 | 설명 |
|:---------|:----:|:------:|:-----|
| `destination` | ✅ | - | 여행지 |
| `start_date` | ✅ | - | 시작일 (YYYY-MM-DD) |
| `end_date` | ✅ | - | 종료일 (YYYY-MM-DD) |
| `origin` | ❌ | 인천 | 출발지 |
| `adults` | ❌ | 2 | 성인 인원 |
| `children` | ❌ | 0 | 어린이 인원 |
| `transport` | ❌ | public | car(자차)/public(대중교통)/flight(항공) |
| `themes` | ❌ | - | 테마 리스트 (["맛집", "자연"]) |

---

### 5. `send_to_kakao` - 카카오톡 나에게 보내기

| 파라미터 | 필수 | 기본값 | 설명 |
|:---------|:----:|:------:|:-----|
| `message` | ✅ | - | 전송할 메시지 (여행 일정 등) |
| `title` | ❌ | 🗺️ 여행 플래너 | 메시지 제목 |
| `access_token` | ❌ | 환경변수 | 카카오 로그인 Access Token |

⚠️ **카카오 로그인 Access Token 필요**
- 카카오 개발자 콘솔 → 앱 → 카카오 로그인 활성화
- 동의 항목에서 `talk_message` 추가
- [REST API 테스트](https://developers.kakao.com/tool/rest-api)에서 토큰 발급

---

## 🔧 로컬 개발

### 설치

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 환경변수

```bash
export KAKAO_REST_API_KEY="your_kakao_rest_api_key"
```

### 실행

```bash
# stdio 모드 (로컬 테스트)
python -m src.travel_planner.server

# SSE 모드 (원격 서버)
python -m src.travel_planner.server sse
```

---

## 🌐 배포 (Railway)

### 1. GitHub 레포 생성 후 push

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/travel-planner-mcp.git
git push -u origin main
```

### 2. Railway 프로젝트 생성

1. [Railway](https://railway.app) 접속
2. GitHub 레포 연결
3. 환경변수 설정: `KAKAO_REST_API_KEY`
4. 배포 완료 후 URL 확인

### 3. PlayMCP 등록

- **MCP Endpoint URL:** `https://your-app.railway.app/sse`

---

## 📄 라이선스

MIT License

---

## 👨‍💻 개발자

Made with ❤️ for travelers
