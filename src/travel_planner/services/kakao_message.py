"""카카오톡 메시지 발송 서비스

카카오 로그인 Access Token이 필요합니다.
https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api
"""

import os
import httpx
import json

KAKAO_MESSAGE_API_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


async def send_to_me(
    access_token: str,
    title: str,
    description: str,
    button_title: str = "자세히 보기",
    button_url: str = "https://map.kakao.com/"
) -> dict:
    """
    나에게 카카오톡 메시지를 발송합니다.
    
    Args:
        access_token: 카카오 로그인 Access Token
        title: 메시지 제목
        description: 메시지 내용
        button_title: 버튼 텍스트
        button_url: 버튼 클릭 시 이동할 URL
    
    Returns:
        API 응답
    """
    if not access_token:
        raise ValueError("카카오 로그인 Access Token이 필요합니다.")
    
    # 텍스트 템플릿 (가장 간단한 형태)
    template_object = {
        "object_type": "text",
        "text": f"📍 {title}\n\n{description}",
        "link": {
            "web_url": button_url,
            "mobile_web_url": button_url
        },
        "button_title": button_title
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "template_object": json.dumps(template_object)
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            KAKAO_MESSAGE_API_URL,
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            return {"success": True, "result": response.json()}
        else:
            error_data = response.json()
            return {
                "success": False, 
                "error_code": error_data.get("code"),
                "error_message": error_data.get("msg", "알 수 없는 오류")
            }


async def send_feed_to_me(
    access_token: str,
    title: str,
    description: str,
    image_url: str | None = None,
    link_url: str = "https://map.kakao.com/",
    buttons: list[dict] | None = None
) -> dict:
    """
    나에게 피드형 카카오톡 메시지를 발송합니다.
    
    Args:
        access_token: 카카오 로그인 Access Token
        title: 메시지 제목
        description: 메시지 설명
        image_url: 이미지 URL (선택)
        link_url: 링크 URL
        buttons: 버튼 리스트 (선택)
    
    Returns:
        API 응답
    """
    if not access_token:
        raise ValueError("카카오 로그인 Access Token이 필요합니다.")
    
    # 피드 템플릿
    template_object = {
        "object_type": "feed",
        "content": {
            "title": title,
            "description": description,
            "link": {
                "web_url": link_url,
                "mobile_web_url": link_url
            }
        }
    }
    
    # 이미지 추가
    if image_url:
        template_object["content"]["image_url"] = image_url
        template_object["content"]["image_width"] = 640
        template_object["content"]["image_height"] = 640
    
    # 버튼 추가
    if buttons:
        template_object["buttons"] = buttons
    else:
        template_object["buttons"] = [
            {
                "title": "지도에서 보기",
                "link": {
                    "web_url": "https://map.kakao.com/",
                    "mobile_web_url": "https://map.kakao.com/"
                }
            }
        ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "template_object": json.dumps(template_object)
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            KAKAO_MESSAGE_API_URL,
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            return {"success": True, "result": response.json()}
        else:
            error_data = response.json()
            return {
                "success": False, 
                "error_code": error_data.get("code"),
                "error_message": error_data.get("msg", "알 수 없는 오류")
            }

