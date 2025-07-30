import requests
import base64
import json
from typing import Optional


def _video_file_to_base64(video_path: str) -> Optional[str]:
    """
    将视频文件转换为BASE64编码
    
    Args:
        video_path: 视频文件路径
    
    Returns:
        str: BASE64编码的视频数据，如果失败返回None
    """
    try:
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            return video_base64
    except Exception as e:
        print(f"视频文件转换失败: {e}")
        return None

def video2txt(
    api_key,
    video_path, 
    prompt_text,
    base_url="https://generativelanguage.googleapis.com/v1beta",
    model: str = "gemini-2.0-flash",
    proxy=None
):
    video_data = _video_file_to_base64(video_path)
    if video_data is None:
        print("无法读取视频文件或转换为BASE64")
        return None
    
    # 构建完整的API URL
    url = f"{base_url}/models/{model}:generateContent?key={api_key}"
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 构建请求体
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "video/mp4",
                        "data": video_data
                    }
                },
                {"text": prompt_text}
            ]
        }]
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 如果状态码不是2xx会抛出异常
        
        # 解析响应
        result = response.json()
        
        # 提取处理结果
        if (result.get("candidates") and 
            len(result["candidates"]) > 0 and 
            result["candidates"][0].get("content") and
            result["candidates"][0]["content"].get("parts") and
            len(result["candidates"][0]["content"]["parts"]) > 0):
            
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print("响应格式异常，无法提取结果")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return None

