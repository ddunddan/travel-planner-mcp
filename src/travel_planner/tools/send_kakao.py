"""카카오톡 나에게 메시지 보내기 Tool

카카오 로그인 Access Token이 필요합니다.
"""

import os
from ..services.kakao_message import send_to_me, send_feed_to_me


async def send_to_kakao(
    message: str,
    title: str = "🗺️ 여행 플래너",
    access_token: str | None = None
) -> str:
    """
    여행 일정을 카카오톡 나에게 보내기로 전송합니다.
    
    ⚠️ 카카오 로그인 Access Token이 필요합니다.
    
    Args:
        message: 전송할 메시지 내용 (여행 일정 등)
        title: 메시지 제목 (기본: "🗺️ 여행 플래너")
        access_token: 카카오 로그인 Access Token (선택, 환경변수에서 가져올 수도 있음)
    
    Returns:
        전송 결과
    """
    # Access Token 확인
    token = access_token or os.getenv("KAKAO_ACCESS_TOKEN")
    
    if not token:
        return """❌ 카카오톡 메시지 전송 실패

🔑 카카오 로그인 Access Token이 필요합니다.

📋 Access Token 발급 방법:
1. 카카오 개발자 콘솔 접속: https://developers.kakao.com/
2. 앱 선택 → [카카오 로그인] 활성화
3. [동의 항목]에서 'talk_message' 추가
4. [도구] → [REST API 테스트]에서 토큰 발급
5. 발급받은 Access Token을 환경변수로 설정:
   export KAKAO_ACCESS_TOKEN="your_access_token"

💡 또는 access_token 파라미터로 직접 전달해주세요."""
    
    # 메시지 길이 제한 (카카오톡 텍스트 템플릿: 200자)
    # 너무 긴 메시지는 요약
    if len(message) > 1000:
        # 긴 메시지는 피드 템플릿 사용 (설명: 최대 4줄)
        summary = _summarize_trip(message)
        
        try:
            result = await send_feed_to_me(
                access_token=token,
                title=title,
                description=summary,
                link_url="https://map.kakao.com/"
            )
            
            if result["success"]:
                return f"""✅ 카카오톡 전송 완료!

📱 카카오톡 '나와의 채팅'을 확인하세요.

📋 전송된 내용:
{title}
{summary[:200]}..."""
            else:
                return f"❌ 전송 실패: {result.get('error_message', '알 수 없는 오류')}"
                
        except Exception as e:
            return f"❌ 전송 중 오류 발생: {str(e)}"
    
    else:
        # 짧은 메시지는 텍스트 템플릿
        try:
            result = await send_to_me(
                access_token=token,
                title=title,
                description=message[:200],
                button_title="지도에서 보기",
                button_url="https://map.kakao.com/"
            )
            
            if result["success"]:
                return f"""✅ 카카오톡 전송 완료!

📱 카카오톡 '나와의 채팅'을 확인하세요."""
            else:
                return f"❌ 전송 실패: {result.get('error_message', '알 수 없는 오류')}"
                
        except Exception as e:
            return f"❌ 전송 중 오류 발생: {str(e)}"


def _summarize_trip(full_message: str) -> str:
    """긴 여행 일정을 요약합니다."""
    lines = full_message.split('\n')
    
    # 핵심 정보만 추출
    summary_parts = []
    
    for line in lines:
        # 여행 기본 정보
        if any(x in line for x in ['📅', '👥', '🚀', '📍']):
            clean_line = line.strip()
            if clean_line:
                summary_parts.append(clean_line)
        
        # Day 정보
        if 'Day' in line and '📌' in line:
            summary_parts.append(line.strip())
    
    # 최대 4줄로 제한
    summary = '\n'.join(summary_parts[:6])
    
    if len(summary) > 200:
        summary = summary[:197] + "..."
    
    return summary

