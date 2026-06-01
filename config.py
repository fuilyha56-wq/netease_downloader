"""网易云下载插件配置"""

from src.core.components.base import BaseConfig
from src.core.components.base.config import config_section, Field, SectionBase


class NeteaseConfig(BaseConfig):
    config_name = "config"
    config_description = "网易云音乐下载插件配置"

    @config_section("general")
    class GeneralSection(SectionBase):
        download_dir: str = Field(
            default="data/netease_cache",
            description="默认下载目录（永久存储）"
        )
        temp_dir: str = Field(
            default="data/netease_cache/temp",
            description="临时文件目录（供 SVC 等临时使用）"
        )
        request_timeout: int = Field(default=15, description="HTTP 请求超时秒数")
        max_concurrent: int = Field(default=3, description="最大并发下载数")
        retry_times: int = Field(default=2, description="下载失败重试次数")

    @config_section("cookies")
    class CookiesSection(SectionBase):
        cookie_raw: str = Field(
            default="",
            description="从 cookie-editor 导出的 Cookie 内容（支持 JSON / Header String / Netscape 格式）"
        )
        netease_cookie: str = Field(
            default="",
            description="手动填写的 Cookie 字符串，如 'MUSIC_U=xxx; __csrf=xxx'（若 cookie_raw 提供则忽略）"
        )
        netease_cookie_file: str = Field(
            default="",
            description="网易云音乐 cookies.txt 文件路径（若 cookie_raw 或 netease_cookie 提供则忽略）"
        )

    @config_section("quality")
    class QualitySection(SectionBase):
        default_quality: str = Field(
            default="standard",
            description="默认音质: standard(128k) / higher(320k) / exhigh(flac)"
        )
        allow_quality_fallback: bool = Field(default=True)

    general: GeneralSection = Field(default_factory=GeneralSection)
    cookies: CookiesSection = Field(default_factory=CookiesSection)
    quality: QualitySection = Field(default_factory=QualitySection)