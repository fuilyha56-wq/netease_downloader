"""测试命令：下载歌曲并发送文件（已适配框架 Command 参数）"""

from src.core.components.base import BaseCommand
from src.core.components.types import ChatType, PermissionLevel
from src.app.plugin_system.api import send_api, service_api
from src.kernel.logger import get_logger

logger = get_logger("test_download_cmd")

class TestDownloadCommand(BaseCommand):
    command_name = "下载测试"
    command_description = "测试网易云下载功能"
    permission_level = PermissionLevel.USER
    chat_type = ChatType.ALL
    command_prefix = "/"

    def __init__(self, plugin, stream_id: str, message_id: str = "", message=None):
        super().__init__(plugin, stream_id, message_id, message)
        self.config = plugin.config

    async def execute(self, message_text: str) -> tuple[bool, str]:
        # message_text 已经是参数部分，例如 "灵秀" 或 "<灵秀>"
        song_name = message_text.strip()
        if not song_name:
            await send_api.send_text("用法：/下载测试 <歌曲名>", self.stream_id)
            return False, "参数不足"
        
        # 去除用户可能手打的尖括号
        if song_name.startswith('<') and song_name.endswith('>'):
            song_name = song_name[1:-1]
        
        downloader = service_api.get_service("netease_downloader:service:downloader")
        if not downloader:
            await send_api.send_text("❌ 下载服务未加载", self.stream_id)
            return False, "服务不可用"

        await send_api.send_text(f"🎵 正在搜索并下载《{song_name}》，请稍候...", self.stream_id)

        success, result = await downloader.download_by_keyword(
            keyword=song_name,
            is_temp=False,
        )

        if not success:
            await send_api.send_text(f"❌ 下载失败：{result}", self.stream_id)
            return False, result

        file_path = result
        send_ok = await send_api.send_file(
            file_path=file_path,
            stream_id=self.stream_id,
            file_name=f"{song_name}.mp3"
        )
        if send_ok:
            await send_api.send_text(f"✅ 《{song_name}》下载完成！", self.stream_id)
            return True, file_path
        else:
            await send_api.send_text("❌ 文件发送失败（可能过大或网络问题）", self.stream_id)
            return False, "发送失败"