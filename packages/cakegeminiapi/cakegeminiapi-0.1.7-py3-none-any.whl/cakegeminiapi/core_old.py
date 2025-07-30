import os
import time
from tqdm import tqdm

import google.generativeai as genai
import httplib2
import urllib3

def set_proxy(proxy_url=None):
    """设置全局代理"""
    if proxy_url:
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        # 为 httplib2 设置代理
        httplib2.Http.proxy_info = httplib2.ProxyInfo(
            proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
            proxy_host=proxy_url.split(':')[0],
            proxy_port=int(proxy_url.split(':')[1]) if ':' in proxy_url else 80
        )
        # 为 urllib3 设置代理
        urllib3.make_headers(proxy_basic_auth=None)

def video2txt(api_key, video_path, prompt_text, proxy=None):
    """Analyzes a video to get a summary and breakdown into key scenes."""
    # 设置代理
    set_proxy(proxy)
    
    genai.configure(api_key=api_key)
    from google import genai as genai2

    client = genai2.Client()
    from google.genai import types

    video_bytes = open(video_path, 'rb').read()
    print(f"Video file size: {len(video_bytes)} bytes")

    # 相关接口见：
    # 1. 接入 https://ai.google.dev/gemini-api/docs/quickstart?hl=zh-cn
    # 2. 视频分析 https://ai.google.dev/gemini-api/docs/video-understanding?hl=zh-cn
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=types.Content(
            parts=[
                types.Part(
                    inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
                ),
                types.Part(text=prompt_text)
            ]
        )
    )
    print(f"Response received: {response}")

    return response.text
