# Netease Downloader Plugin

网易云音乐下载插件 — 提供按需下载歌曲的服务，支持免费歌曲下载，VIP 歌曲需有效 Cookie（好吧VIP歌好像下不了）。

## 功能特性

- 根据歌曲名称自动搜索并下载 MP3 音频
- 支持**精确搜索**：用双引号包裹短语（如 `"曲名 歌手"`）提高匹配准确率
- 自动重命名文件为 `歌手 - 歌名.mp3`（可读格式）
- 提供 `Service` 组件，供其他插件调用（可实现批量下载、自定义目录、临时文件管理）
- 内置测试命令 `/下载测试 <歌曲名>`（仅用于演示和调试）
- 支持 Netscape 格式的 Cookie 文件（用于下载 VIP 歌曲）
- 自动跳过 VIP/付费歌曲（若未提供有效 Cookie）

## 安装

1. 将 `netease_downloader` 文件夹放入 `plugins/` 目录
2. 重启机器人或执行 `/reload_plugin netease_downloader`
3. 配置 Cookie

## 配置

配置文件路径：`data/config/netease_downloader/config.toml`（首次运行后自动生成）

### Cookie 配置（可选）

如需下载 VIP 歌曲，请提供网易云账号的有效 Cookie：

1. 使用浏览器扩展 **Cookie-Editor**（[Edge](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi) / [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)）
2. 登录 [music.163.com](https://music.163.com)
3. 点击 Cookie-Editor 图标 → **Export** → **Netscape** 格式
4. 保存为 `netease_cookies.txt`（任意路径）
5. 在 `config.toml` 中设置路径：

```toml
[cookies]
netease_cookie_file = "C:/path/to/netease_cookies.txt"

注意：Cookie 有有效期，过期后需要重新导出。

其他配置
toml
[general]
download_dir = "data/netease_cache"   # 永久下载目录
temp_dir = "data/netease_cache/temp"  # 临时文件目录
request_timeout = 15                  # 请求超时（秒）
retry_times = 2                       # 下载失败重试次数
使用方式
1. 测试命令（仅用于调试）
在聊天中发送：

text
/下载测试 xxx
/下载测试 "xxx xxx"
机器人将搜索、下载并发送文件。文件名格式为 歌手 - 歌名.mp3。

提示：测试命令仅用于验证下载功能，实际插件开发请使用下方的 Service。

2. 在其他插件中调用 Service（推荐）
python
from src.app.plugin_system.api import service_api

downloader = service_api.get_service("netease_downloader:service:downloader")
if downloader:
    success, file_path = await downloader.download_by_keyword(
        keyword="晴天",
        is_temp=True       # 下载到临时目录
    )
    if success:
        # 处理音频文件...
        await downloader.clean_temp_file(file_path)  # 清理临时文件
可用方法：

download_by_keyword(keyword, output_dir=None, is_temp=False)

自动搜索并下载最匹配的歌曲。

keyword 支持精确短语（如 "歌曲名 歌手"），提高准确率。

download_by_id(song_id, output_dir=None, is_temp=False, song_name=None, artist=None)

通过歌曲 ID 下载，可指定文件名。

clean_temp_file(file_path)：删除临时文件。

常见问题
下载的文件只有 100KB 且无法播放？
说明 Cookie 无效或歌曲为 VIP 限制。请重新导出 Cookie 或换用免费歌曲测试。

测试命令 /下载测试 起风了 应能正常下载（免费歌曲）。

搜索到的歌曲名不匹配？
使用精确搜索语法：/下载测试 "歌名 歌手"（双引号包裹）。

如何获取歌曲 ID？
在网易云网页版打开歌曲页面，URL 中的 id 参数即为歌曲 ID。

测试命令下载成功后，文件名显示不正确？
测试命令显示的消息是固定的，实际保存的文件名已经是 歌手 - 歌名.mp3（可检查下载目录）。

消息提示不准确是临时测试命令的局限，不影响实际文件。

注意事项
本插件仅供个人学习使用，请勿用于商业或侵权用途。

下载 VIP 歌曲需自行拥有有效的网易云 VIP 账号。

Cookie 文件请妥善保管，不要公开分享。



netease_downloader/
├── manifest.json
├── plugin.py
├── config.py
├── api.py
├── service.py
├── utils.py
├── commands/
│   └── test_download.py
└── README.md
