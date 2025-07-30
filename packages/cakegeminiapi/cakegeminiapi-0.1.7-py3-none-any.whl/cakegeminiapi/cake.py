import os
from .core import video2txt as inner_video2txt
from .prompts import PROMPT_VIDEO_Commentator

class CakeGeminiAPI:
    def __init__(self, api_key, base_url, proxy=None):
        self.base_url = base_url
        self.api_key = api_key
        self.proxy = proxy

    def video2txt(self, video_path, prompt_text):
        """
        给定视频和提示词，完成提示词要求的任务
        """
        return inner_video2txt(
            api_key=self.api_key,
            video_path=video_path,
            prompt_text=prompt_text,
            base_url=self.base_url,
            proxy=self.proxy
        )

    def video_commentator(self, video_path):
        """
        视频解说员
        """
        response_text = inner_video2txt(
            api_key=self.api_key,
            video_path=video_path,
            prompt_text=PROMPT_VIDEO_Commentator,
            base_url=self.base_url,
            proxy=self.proxy
        )

        # 提取其中的 “```” 包裹的内容
        if "```" in response_text:
            start = response_text.index("```") + 3
            end = response_text.index("```", start)
            return response_text[start:end].strip()
        
        return response_text.strip()  # 如果没有代码块，直接返回原始文本

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CakeGeminiAPI Video Commentator")
    parser.add_argument("-u", "--base_url", type=str, required=False, help="Base URL For Gemini API requests. Default is https://generativelanguage.googleapis.com/v1beta. You can set GOOGLE_API_URL environment variable to override this.")
    parser.add_argument("-k", "--api_key", type=str, required=False, help="Google API key for Gemini. https://aistudio.google.com/apikey")
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument("-p", "--proxy", type=str, default=None, help="Proxy server URL (optional)")

    args = parser.parse_args()

    base_url = args.base_url if args.base_url else os.getenv("GOOGLE_API_URL", "https://generativelanguage.googleapis.com/v1beta")
    api_key = args.api_key if args.api_key else os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key is required. Please set the GOOGLE_API_KEY environment variable or use the -k option.")
    api = CakeGeminiAPI(base_url=base_url, api_key=api_key, proxy=args.proxy)
    result = api.video_commentator(args.video_path)
    print(result)

if __name__ == "__main__":
    main()