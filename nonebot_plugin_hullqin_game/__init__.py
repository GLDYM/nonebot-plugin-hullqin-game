from nonebot.plugin import PluginMetadata
from .config import Config, config

__plugin_meta__ = PluginMetadata(
    name="Hullqin Game 桌游发车",
    description="Hullqin Game 桌游发车",
    usage="""▶ 发车 <游戏名称> [房间ID]：发起新的桌游
  ▷ 不填游戏名称会显示游戏列表
▶ 查车：查看本群的桌游
▶ 封车 <序号>：关闭指定的桌游房间
▶ 封车 <游戏名称> <房间ID>：关闭指定的桌游房间
""",
    type="application",
    homepage="https://github.com/GLDYM/nonebot-plugin-hullqin-game",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={"author": "Polaris_Light", "version": "1.0.1", "priority": 5},
)

from nonebot import require

require("nonebot_plugin_localstore")

from typing import Union
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    PrivateMessageEvent,
)

from .commands import (
    open_games,
    query_games,
    stop_games,
)

help_cmd = on_command(
    "game_help",
    aliases={"发车帮助", "桌游帮助"},
    force_whitespace=True,
    priority=5,
    block=True,
)

@help_cmd.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await help_cmd.finish(__plugin_meta__.usage)
