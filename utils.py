"""下载工具函数"""

import asyncio
import os
import re
import shutil
from pathlib import Path
from typing import Optional

import aiofiles
import aiohttp
from aiohttp import ClientTimeout, ClientError

from src.kernel.logger import get_logger

logger = get_logger("netease_downloader_utils")


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符（Windows）"""
    illegal_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(illegal_chars, '_', name)
    sanitized = sanitized.strip(' .')
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized


async def download_file(
    url: str,
    output_path: str,
    timeout: int = 30,
    retry: int = 2,
    headers: Optional[dict] = None,
) -> bool:
    """下载文件到本地"""
    if not headers:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com",
        }
    for attempt in range(retry + 1):
        try:
            timeout_obj = ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                        async with aiofiles.open(output_path, "wb") as f:
                            while True:
                                chunk = await resp.content.read(8192)
                                if not chunk:
                                    break
                                await f.write(chunk)
                        logger.info(f"下载成功: {output_path}")
                        return True
                    else:
                        logger.warning(f"下载失败 HTTP {resp.status}: {url}")
        except (ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"下载尝试 {attempt+1}/{retry+1} 失败: {e}")
            if attempt < retry:
                await asyncio.sleep(1)
    return False


async def ensure_dir(path: str) -> None:
    """确保目录存在（异步兼容）"""
    Path(path).mkdir(parents=True, exist_ok=True)


def clean_temp_file(file_path: str) -> None:
    """删除临时文件（供调用方使用）"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"已删除临时文件: {file_path}")
    except Exception as e:
        logger.warning(f"删除临时文件失败 {file_path}: {e}")


def clean_temp_dir(temp_dir: str) -> None:
    """清空整个临时目录（谨慎使用）"""
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"清理临时目录失败: {e}")