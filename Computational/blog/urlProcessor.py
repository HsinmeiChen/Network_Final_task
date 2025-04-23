from enum import Enum
from urllib.parse import urlparse, parse_qs
import re

# 定义平台枚举
class Platform(Enum):
    YOUTUBE = "Youtube"
    GOOGLE_DRIVE = "GoogleDrive"

@staticmethod
def extract_specific_urls(text, keywords):
    # 用來存儲所有匹配到的 URL
    all_urls = []

    # 遍歷關鍵字列表
    for keyword in keywords:
        # 使用正則表達式來匹配包含指定字串的 URL
        url_pattern = rf'(https?://[^\s<]*{keyword}[^\s<]*)'
        urls = re.findall(url_pattern, text)
        
        # 如果找到符合條件的 URL，加入到 all_urls 列表中
        if urls:
            all_urls.extend(urls)
    
    # 如果有匹配的 URL，返回它們
    if all_urls:
        return all_urls
    return None  # 如果沒有找到符合條件的 URL，返回 None

@staticmethod
def convert_google_drive_viewURL_To_embeddedURL(view_url):
    # 确认 URL 是否符合需要转换的格式
    if "drive.google.com/file/d/" in view_url:
        # 提取 file_id 部分
        file_id = view_url.split("/d/")[1].split("/")[0]
        # 构造嵌入式预览 URL
        preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
        return preview_url
    else:
        return "Invalid URL"
@staticmethod
def convert_youtube_viewURL_To_embeddedURL(view_url):
    # 解析 URL
    parsed_url = urlparse(view_url)
    # 解析 URL 的查询参数
    query_params = parse_qs(parsed_url.query)
    
    # 提取 'v' 参数（视频 ID）
    video_id = query_params.get('v')
    
    if video_id:
        # 构造嵌入式 URL
        embed_url = f"https://www.youtube.com/embed/{video_id[0]}"
        return embed_url
    else:
        return "Invalid URL or video ID not found"
    
@staticmethod
def convert_viewURLs_to_embeddedURLs(urls):
    if urls:
        converted_urls = []
        for url in urls:
            if "youtube.com" in url:
                converted_urls.append(convert_youtube_viewURL_To_embeddedURL(url))
            elif "drive.google.com" in url:
                converted_urls.append(convert_google_drive_viewURL_To_embeddedURL(url))
            else:
                converted_urls.append("Unsupported platform or invalid URL")
        return converted_urls
    return None
