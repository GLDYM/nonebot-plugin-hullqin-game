from pydantic import BaseModel

from nonebot import get_plugin_config

# fmt:off
class Config(BaseModel):
    room_expired_time: int = 1200  # 招募信息过期时间，单位：秒
    playwright_headless: bool = True  # Playwright 是否无头模式
# fmt:on

config = get_plugin_config(Config)