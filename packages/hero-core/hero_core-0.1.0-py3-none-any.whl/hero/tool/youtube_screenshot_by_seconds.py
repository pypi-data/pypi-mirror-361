from typing import Any, Dict, List, Optional
import traceback
from util import log, config, function, agent, stream
import tool
import os
import re
import json
import requests
import cv2
import time
import subprocess
import hashlib
import numpy as np
import yt_dlp

class YoutubeScreenshotBySeconds:
    """
    可以按指定秒数（和3秒前后）从YouTube视频中抓取截图，并写入独立文件。
    """
    def __init__(self):
        self.name = "youtube_screenshot_by_seconds"
        self.prompt = """
<tool name="youtube_screenshot_by_seconds">
    <desc>Can capture screenshots from a YouTube video at specified seconds (and 3 seconds around) and write them to an independent file.</desc>
    <params>
        <url type="string">The URL of the YouTube video</url>
        <second_list type="list">The time in seconds to get the screenshot</second_list>
    </params>
    <example>
        {
            "tool": "youtube_screenshot_by_seconds",
            "params": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "second_list": [10, 20, 30]
            }
        }
    </example>
</tool>
        """

    def get_name(self):
        """
        获取工具名称
        """
        return self.name

    def get_prompt(self):
        """
        获取工具提示
        """
        return self.prompt

    async def invoke(self, params: Dict[str, Any], caller: Dict[str, str]) -> Dict[str, str]:
        """
        执行工具
        """
        try:
            url = params["url"]
            second_list = params["second_list"]

            if not url:
                raise Exception("URL不能为空")

            if not second_list:
                raise Exception("second_list不能为空")

            if not isinstance(second_list, list):
                raise Exception("second_list必须是列表")

            if not all(isinstance(item, int) for item in second_list):
                raise Exception("second_list中的元素必须是整数")

            if not all(item >= 0 for item in second_list):
                raise Exception("second_list中的元素必须大于等于0")

            screenshot_paths = get_multiple_screenshots(
                url, second_list, caller.get("dir") or ""
            )

            message = f"Saved screenshots: {screenshot_paths}"

            return {
                "status": "success",
                "message": message,
            }

        except Exception as e:
            log.error(f"执行工具失败: {e}")
            raise e

class VideoDownloader:
    def __init__(self, cache_dir="video_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        log.info(f"视频缓存目录: {cache_dir}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # 计算下载进度
            if 'total_bytes' in d:
                progress = d['downloaded_bytes'] / d['total_bytes'] * 100
            elif 'total_bytes_estimate' in d:
                progress = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            else:
                progress = 0

            # 计算下载速度
            speed = d.get('speed', 0)
            if speed:
                speed_str = f"{speed/1024/1024:.1f} MB/s"
            else:
                speed_str = "N/A"

            # 打印进度信息
            print(f"\r下载进度: {progress:.1f}%", flush=True)
        elif d['status'] == 'finished':
            print("\n下载完成，正在处理...")

    def get_video_path(self, video_url):
        """获取视频文件路径，如果已缓存则直接返回，否则下载"""
        # 生成视频URL的哈希值作为文件名
        video_hash = hashlib.md5(video_url.encode()).hexdigest()
        video_path = os.path.join(self.cache_dir, f"{video_hash}.mp4")

        if os.path.exists(video_path):
            log.info(f"使用缓存的视频文件: {video_path}")
            return video_path

        log.info(f"开始下载视频: {video_url}")
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': video_path,
                'noplaylist': True,
                'progress_hooks': [self.progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            log.info("视频下载成功")
            return video_path
        except Exception as e:
            log.error(f"下载视频失败: {str(e)}")
            raise Exception("无法下载视频")


def get_youtube_screenshot(video_url, timestamp, video_downloader, max_retries=3):
    """
    从YouTube视频获取指定时间点的截图
    Args:
        video_url (str): YouTube视频URL
        timestamp (int): 时间戳（秒）
        video_downloader (VideoDownloader): 视频下载器实例
        max_retries (int): 最大重试次数
    Returns:
        numpy.ndarray: 截图图像
    """
    log.info(f"开始处理视频 {video_url} 在 {timestamp} 秒的截图")

    for attempt in range(max_retries):
        try:
            # 获取视频文件路径
            video_path = video_downloader.get_video_path(video_url)

            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("无法打开视频文件")

            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            log.info(
                f"视频信息 - 分辨率: {width}x{height}, FPS: {fps}, 总帧数: {total_frames}, 时长: {duration:.2f}秒"
            )

            # 设置视频位置到指定时间戳
            frame_number = int(timestamp * fps)
            if frame_number >= total_frames:
                log.error(f"时间戳 {timestamp} 超出视频长度 {duration:.2f} 秒")
                return None

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            log.info(f"定位到第 {frame_number} 帧 (时间戳: {timestamp} 秒)")

            # 读取帧
            ret, frame = cap.read()
            cap.release()

            if ret:
                # 确保图像是RGB格式
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                log.info("成功获取视频帧")
                return frame
            else:
                raise Exception("无法获取指定时间点的帧")

        except Exception as e:
            log.error(f"发生错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                log.info("等待2秒后重试...")
                time.sleep(2)
                continue
            else:
                log.error(f"在{max_retries}次尝试后仍然失败")
                raise Exception(f"在{max_retries}次尝试后仍然失败")
            return None


def save_screenshot(frame, output_path):
    """
    保存截图到指定路径
    Args:
        frame (numpy.ndarray): 图像帧
        output_path (str): 输出文件路径
    """
    if frame is not None:
        # 确保图像是RGB格式
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            # 如果图像是BGR格式，转换为RGB
            if frame.dtype == np.uint8:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 使用最高质量的JPEG保存
        cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        log.info(f"截图已保存到: {output_path}")
    else:
        log.error("无法保存截图")


def get_multiple_screenshots(video_url, timestamps, output_dir="screenshots"):
    """
    获取多个时间点的截图
    Args:
        video_url (str): YouTube视频URL
        timestamps (list): 时间戳列表（秒）
        output_dir (str): 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    log.info(f"创建输出目录: {output_dir}")

    # 获取视频ID
    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
    if video_id:
        video_id = video_id.group(1)
    else:
        video_id = "unknown"

    # 创建视频下载器
    video_downloader = VideoDownloader()

    output_paths = []

    extend_timestamps = []
    for timestamp in timestamps:
        extend_timestamps.append(timestamp - 3)
        extend_timestamps.append(timestamp - 2)
        extend_timestamps.append(timestamp - 1)
        extend_timestamps.append(timestamp)
        extend_timestamps.append(timestamp + 1)
        extend_timestamps.append(timestamp + 2)
        extend_timestamps.append(timestamp + 3)

    # 排序、去重
    extend_timestamps = list(set(extend_timestamps))
    extend_timestamps.sort()

    # 处理每个时间戳
    for timestamp in extend_timestamps:
        try:
            frame = get_youtube_screenshot(video_url, timestamp, video_downloader)
            if frame is not None:
                # 生成输出文件名
                output_filename = f"{video_id}_{timestamp}s.jpg"
                output_path = os.path.join(output_dir, output_filename)
                save_screenshot(frame, output_path)
                output_paths.append(output_filename)
        except Exception as e:
            log.error(f"处理时间戳 {timestamp} 时发生错误: {str(e)}")

    return output_paths

tool.hub.register(YoutubeScreenshotBySeconds)