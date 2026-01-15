"""대화 Context 관리 - 여행 정보 누적 저장"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class TravelContext:
    """여행 정보 Context"""
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    adults: int = 2
    children: int = 0
    transport: str = "car"
    themes: list[str] = field(default_factory=list)
    accommodation: Optional[str] = None
    
    # 메타 정보
    last_updated: Optional[str] = None
    confirmed: bool = False
    
    def update(self, **kwargs) -> list[str]:
        """정보 업데이트 및 변경된 필드 반환"""
        changed = []
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                old_value = getattr(self, key)
                if old_value != value:
                    setattr(self, key, value)
                    changed.append(key)
        
        if changed:
            self.last_updated = datetime.now().isoformat()
        
        return changed
    
    def get_missing_required(self) -> list[str]:
        """필수 정보 중 누락된 항목 반환"""
        missing = []
        if not self.destination:
            missing.append("여행지")
        if not self.start_date:
            missing.append("시작일")
        if not self.end_date:
            missing.append("종료일")
        return missing
    
    def is_complete(self) -> bool:
        """필수 정보가 모두 있는지 확인"""
        return len(self.get_missing_required()) == 0
    
    def to_summary(self) -> str:
        """현재까지 확정된 정보 요약"""
        lines = []
        lines.append("📋 [현재까지 확정된 여행 정보]")
        lines.append("")
        
        # 여행지
        if self.destination:
            lines.append(f"   🎯 여행지: {self.destination}")
        else:
            lines.append("   🎯 여행지: (미정)")
        
        # 일정
        if self.start_date and self.end_date:
            lines.append(f"   📅 일정: {self.start_date} ~ {self.end_date}")
        elif self.start_date:
            lines.append(f"   📅 시작일: {self.start_date} (종료일 미정)")
        else:
            lines.append("   📅 일정: (미정)")
        
        # 인원
        pax = f"성인 {self.adults}명"
        if self.children > 0:
            pax += f", 어린이 {self.children}명"
        lines.append(f"   👥 인원: {pax}")
        
        # 이동수단
        transport_names = {"car": "자차/렌트카", "public": "대중교통"}
        lines.append(f"   🚗 이동수단: {transport_names.get(self.transport, self.transport)}")
        
        # 테마
        if self.themes:
            lines.append(f"   🎨 선호 테마: {', '.join(self.themes)}")
        
        # 숙소
        if self.accommodation:
            lines.append(f"   🏨 숙소: {self.accommodation}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "adults": self.adults,
            "children": self.children,
            "transport": self.transport,
            "themes": self.themes,
            "accommodation": self.accommodation,
        }


# 전역 Context 저장소 (세션별)
_contexts: dict[str, TravelContext] = {}


def get_context(session_id: str = "default") -> TravelContext:
    """세션별 Context 가져오기 (없으면 생성)"""
    if session_id not in _contexts:
        _contexts[session_id] = TravelContext()
    return _contexts[session_id]


def clear_context(session_id: str = "default") -> None:
    """Context 초기화"""
    if session_id in _contexts:
        del _contexts[session_id]


def parse_user_input(text: str) -> dict:
    """사용자 입력에서 여행 정보 추출"""
    import re
    
    result = {}
    
    # 날짜 패턴 (YYYY-MM-DD 또는 M월 D일)
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    dates = re.findall(date_pattern, text)
    if len(dates) >= 2:
        result['start_date'] = dates[0]
        result['end_date'] = dates[1]
    elif len(dates) == 1:
        result['start_date'] = dates[0]
    
    # 인원 패턴
    adult_pattern = r'성인\s*(\d+)\s*명'
    adult_match = re.search(adult_pattern, text)
    if adult_match:
        result['adults'] = int(adult_match.group(1))
    
    child_pattern = r'어린이\s*(\d+)\s*명'
    child_match = re.search(child_pattern, text)
    if child_match:
        result['children'] = int(child_match.group(1))
    
    # 이동수단
    if '자차' in text or '렌트카' in text or '렌트' in text:
        result['transport'] = 'car'
    elif '대중교통' in text or '버스' in text or '지하철' in text:
        result['transport'] = 'public'
    
    # 테마 키워드
    themes = []
    theme_keywords = {
        '맛집': '맛집', '음식': '맛집', '먹거리': '맛집',
        '자연': '자연', '힐링': '자연', '산': '자연', '바다': '자연',
        '역사': '역사', '문화': '역사', '유적': '역사',
        '카페': '카페', '디저트': '카페',
        '쇼핑': '쇼핑',
        '가족': '가족', '아이': '가족',
    }
    for keyword, theme in theme_keywords.items():
        if keyword in text and theme not in themes:
            themes.append(theme)
    if themes:
        result['themes'] = themes
    
    return result

