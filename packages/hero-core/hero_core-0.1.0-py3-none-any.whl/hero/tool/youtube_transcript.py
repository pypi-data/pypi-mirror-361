from typing import Dict, List, Optional
import traceback
from util import log, config, function, agent, stream
import tool
import os
import re
import json
import requests
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


class YoutubeTranscript:
    def __init__(self):
        self.name = "youtube_transcript"
        self.prompt = """
<tool name="youtube_transcript">
    <desc>Use this tool to get the transcript of a YouTube video.</desc>
    <params>
        <url type="string">The URL of the YouTube video</url>
        <write_file type="string">The file name to write the transcript to</write_file>
    </params>
    <example>
        {
            "tool": "youtube_transcript",
            "params": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "write_file": "transcript.txt"
            }
        }
    </example>
</tool>
        """
        self.language = "en"

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(self, params: Dict[str, str], caller: Dict[str, str]) -> Dict[str, str]:
        """
        获取 YouTube 视频的字幕
        Args:
            url: YouTube 视频 URL
            write_file: 字幕文件名
        Returns:
            包含字幕信息的字典，格式如下：
            {
                'success': bool,
                'transcript': str,  # 纯文本格式的字幕
                'error': str  # 如果失败，包含错误信息
            }
        """
        try:
            url = params["url"]
            write_file = params["write_file"]

            if not url:
                raise ValueError("URL is required")

            if not write_file:
                raise ValueError("Write file is required")

            write_file_path = os.path.join(caller.get("dir") or "", write_file)

            video_id = get_youtube_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")

            # 获取字幕列表
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 尝试获取指定语言的字幕
            try:
                transcript = transcript_list.find_transcript([self.language])
            except:
                # 如果找不到指定语言的字幕，尝试获取自动生成的字幕
                try:
                    transcript = transcript_list.find_transcript(["en"])
                    # 如果找到英文字幕，尝试翻译
                    transcript = transcript.translate(self.language)
                except:
                    raise ValueError("无法找到指定语言的字幕")

            # 获取字幕数据
            transcript_data = transcript.fetch()

            # 使用 TextFormatter 将字幕转换为纯文本
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_data)

            # 将字幕保存到文件
            with open(write_file_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            return {
                "status": "success", 
                "message": f"Transcript saved to {write_file_path}",
            }

        except Exception as e:
            log.error(f"获取 YouTube 视频字幕失败: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }


def get_youtube_video_id(url: str) -> Optional[str]:
    """
    从 YouTube URL 中提取视频 ID
    Args:
        url: YouTube 视频 URL
    Returns:
        视频 ID 或 None（如果无法提取）
    """
    # 匹配各种 YouTube URL 格式
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None 


tool.hub.register(YoutubeTranscript)