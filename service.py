"""网易云下载服务 - 供其他插件调用"""

from pathlib import Path
from typing import Optional, Tuple

from src.core.components.base import BaseService
from src.kernel.logger import get_logger

from .config import NeteaseConfig
from .api import NeteaseAPI
from .utils import ensure_dir, clean_temp_file, sanitize_filename

logger = get_logger("netease_downloader_service")


class DownloadService(BaseService):
    service_name = "downloader"
    service_description = "根据歌曲 ID 或关键词下载网易云音乐"

    def __init__(self, plugin):
        super().__init__(plugin)
        self.config: NeteaseConfig = plugin.config

        # 使用 Netscape cookie 文件路径
        cookie_file = self.config.cookies.netease_cookie_file
        self.api = NeteaseAPI(cookie_file=cookie_file)

        # 确保目录存在（异步，在首次使用时创建）
        import asyncio
        asyncio.create_task(self._ensure_dirs())

    async def _ensure_dirs(self):
        await ensure_dir(self.config.general.download_dir)
        await ensure_dir(self.config.general.temp_dir)

    def _build_filename(self, song_name: str, artist: str) -> str:
        """构建文件名：歌手 - 歌名.mp3"""
        if artist:
            name = f"{artist} - {song_name}"
        else:
            name = song_name
        return sanitize_filename(name) + ".mp3"

    async def download_by_id(
        self,
        song_id: int,
        output_dir: Optional[str] = None,
        is_temp: bool = False,
        song_name: Optional[str] = None,
        artist: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        根据歌曲 ID 下载
        :param song_id: 网易云歌曲 ID
        :param output_dir: 自定义输出目录
        :param is_temp: 是否为临时文件
        :param song_name: 歌曲名（如果提供，用于生成文件名）
        :param artist: 歌手名（如果提供，用于生成文件名）
        :return: (成功标志, 文件路径或错误信息)
        """
        await self._ensure_dirs()

        if output_dir is None:
            base_dir = self.config.general.temp_dir if is_temp else self.config.general.download_dir
        else:
            base_dir = output_dir

        # 确定文件名
        if song_name:
            artist_name = artist or ""
            filename = self._build_filename(song_name, artist_name)
        else:
            filename = f"{song_id}.mp3"

        file_path = Path(base_dir) / filename
        if file_path.exists():
            logger.info(f"文件已存在: {file_path}")
            return True, str(file_path)

        success = await self.api.download_song_by_id(song_id, str(file_path))
        if success:
            return True, str(file_path)
        else:
            # 如果下载失败且文件名是自定义的，尝试删除可能的不完整文件
            if file_path.exists():
                file_path.unlink()
            return False, f"下载失败，可能为 VIP 歌曲或 Cookie 无效"

    async def download_by_keyword(
        self,
        keyword: str,
        output_dir: Optional[str] = None,
        is_temp: bool = False,
    ) -> Tuple[bool, str]:
        """根据关键词搜索并下载第一个可用的歌曲"""
        song_info = await self.api.search_song(keyword)
        if not song_info:
            return False, f"未找到歌曲: {keyword}"
        song_id = song_info["id"]
        song_name = song_info["name"]
        artists = song_info.get("artists", [])
        artist = ", ".join([a["name"] for a in artists]) if artists else ""
        logger.info(f"搜索到歌曲: {song_name} - {artist} (ID: {song_id})")
        return await self.download_by_id(song_id, output_dir, is_temp, song_name, artist)

    async def clean_temp_file(self, file_path: str) -> None:
        clean_temp_file(file_path)