import argparse
import os
import time
import requests
import hashlib
import json
import subprocess
import re # Import the re module
from tqdm import tqdm
from datetime import datetime

import google.generativeai as genai
import httplib2
import urllib3
from .core import video2txt


def ai_video_commentator(api_key, video_path, prompt_text, proxy=None):
    """Generates a video commentary script in SRT format."""
    # 设置代理
    set_proxy(proxy)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash') # Corrected model name

    video_files = upload_video_chunks(video_path)
    
    # Wait for files to become active before using them
    wait_for_files_active(video_files)

    contents = [prompt_text]

    print("Sending request for video commentary generation...")
    response = model.generate_content(contents)
    
    for video_file in video_files:
        genai.delete_file(video_file.name)
    print("Deleted temporary uploaded files.")

    return response.text

def main():
    argparser = argparse.ArgumentParser(description="""Video Analysis""",
    epilog="""-------------------------------
    Example usage:
        geminiapi video_path "your prompt" -k GEMINI_API_KEY --proxy http://127.0.0.1:7890 # 或导出环境变量 GOOGLE_API_KEY
        
    Code sample:
        from geminiapi import video2txt
        output = video2txt(api_key, video_path, prompt_text, proxy="http://127.0.0.1:7890") 
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter
    )

    argparser.add_argument("-u", "--base_url", type=str, required=False, help="Base URL For Gemini API requests. Default is https://generativelanguage.googleapis.com/v1beta. You can set GOOGLE_API_URL environment variable to override this.")
    argparser.add_argument("-k", "--api_key", type=str, required=False, help="Google API key for Gemini. https://aistudio.google.com/apikey")
    argparser.add_argument("video_path", type=str, help="Path to the video file.")
    argparser.add_argument("prompt_text", type=str, help="Prompt text for video analysis.")
    argparser.add_argument("--proxy", type=str, help="Proxy URL (e.g., http://127.0.0.1:7890)")
    
    args = argparser.parse_args()


    base_url = args.base_url if args.base_url else os.getenv("GOOGLE_API_URL", "https://generativelanguage.googleapis.com/v1beta")
    api_key = args.api_key if args.api_key else os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key is required. Please set the GOOGLE_API_KEY environment variable or use the -k option.")
    
    video_path = args.video_path
    prompt_text = args.prompt_text
    proxy = args.proxy if args.proxy else os.getenv("HTTP_PROXY")
    
    output = video2txt(
        api_key=api_key,
        video_path=video_path,
        prompt_text=prompt_text,
        base_url=base_url,
        proxy=proxy
    )
    print(output)

if __name__ == "__main__":
    main()