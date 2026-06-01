"""网易云下载插件主类"""

from src.app.plugin_system.api.log_api import get_logger
from src.core.components.base import BasePlugin
from src.core.components.loader import register_plugin

from .config import NeteaseConfig
from .service import DownloadService
from .commands.test_download import TestDownloadCommand   # 测试命令，可保留

logger = get_logger("netease_downloader")


@register_plugin
class NeteaseDownloaderPlugin(BasePlugin):
    plugin_name = "netease_downloader"
    plugin_version = "1.0.0"
    plugin_author = "Your Name"
    plugin_description = "网易云音乐下载插件，提供按需下载服务，支持 VIP 识别"

    configs = [NeteaseConfig]

    def get_components(self) -> list[type]:
        """返回插件包含的组件类列表"""
        return [
            DownloadService,
            TestDownloadCommand,   # 保留测试命令，方便调试
        ]

    async def on_plugin_loaded(self):
        logger.info("网易云下载插件已加载")