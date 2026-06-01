"""网易云音乐 API 封装（搜索 + 直接外链下载）"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp
from aiohttp import ClientTimeout

from src.kernel.logger import get_logger

logger = get_logger("netease_api")


def parse_cookie_file(cookie_file: str) -> Dict[str, str]:
    """解析 Netscape 格式的 cookies.txt 文件"""
    cookies = {}
    if not cookie_file or not Path(cookie_file).exists():
        return cookies
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]
        logger.info(f"从 Netscape 文件加载 {len(cookies)} 个 cookies: {cookie_file}")
    except Exception as e:
        logger.warning(f"解析 cookies 文件失败: {e}")
    return cookies


class NeteaseAPI:
    """网易云 API 客户端（仅搜索 + 直接下载）"""

    def __init__(self, cookie_file: str = ""):
        self._cookies = parse_cookie_file(cookie_file)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Referer": "https://music.163.com",
        }

    async def search_song(self, keyword: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        搜索歌曲，返回第一首可用的歌曲信息（优先免费）
        支持精确短语：如果 keyword 以双引号开头和结尾，则去掉引号后整体搜索（保留内部空格）
        """
        # 处理精确短语
        raw_keyword = keyword.strip()
        if raw_keyword.startswith('"') and raw_keyword.endswith('"'):
            raw_keyword = raw_keyword[1:-1]
            logger.debug(f"精确短语搜索: {raw_keyword}")
        # 否则保持原样（可能包含空格，网易云 API 会按多个词匹配）

        url = "https://music.163.com/api/search/get/web"
        params = {"s": raw_keyword, "type": 1, "limit": limit, "offset": 0}
        timeout = ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(f"搜索失败 HTTP {resp.status}")
                        return None
                    text = await resp.text()
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError as e:
                        logger.error(f"搜索响应 JSON 解析失败: {e}")
                        return None
                    songs = data.get("result", {}).get("songs", [])
                    if not songs:
                        return None
                    # 优先返回免费歌曲 (fee==0)
                    for song in songs:
                        if song.get("fee", 1) == 0:
                            return song
                    return songs[0]
        except Exception as e:
            logger.error(f"搜索歌曲异常: {e}")
            return None

    async def download_song_by_id(self, song_id: int, output_path: str) -> bool:
        """
        直接外链下载歌曲（跟随重定向，验证 Content-Type）
        """
        file_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
        timeout = ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(cookies=self._cookies, timeout=timeout) as session:
                async with session.get(file_url, headers=self.headers, allow_redirects=True) as resp:
                    if resp.status != 200:
                        logger.warning(f"下载失败 HTTP {resp.status}: {file_url}")
                        return False
                    content_type = resp.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        # 返回的是 HTML 错误页（如 VIP 限制或 Cookie 失效）
                        text_preview = (await resp.text())[:200]
                        logger.warning(f"返回 HTML 而非音频: {text_preview}")
                        return False
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    logger.info(f"下载成功: {output_path}")
                    return True
        except Exception as e:
            logger.error(f"下载异常: {e}")
            return False