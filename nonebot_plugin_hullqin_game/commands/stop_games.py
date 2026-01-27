import shlex
from typing import Dict, List, Union

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)

from ..utils.data_manager import data_manager

stop_games = on_command(
    "stop_games", aliases={"封车", "关房", "关闭房间"}, priority=5, block=True
)


@stop_games.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = event.group_id
    args = shlex.split(arg.extract_plain_text())

    group_data = data_manager.load_group_data(group_id)
    if "games" not in group_data or not group_data["games"]:
        await stop_games.send("当前没有任何桌游房间哦~")
        return None
    
    # 此处不应该清除过期房间，会导致索引号混乱 
    # data_manager.remove_expired_games(group_id)
    
    if not args or args == []:
        await stop_games.send("请提供要关闭的房间索引号，或游戏ID和房间ID")
        return None
    if len(args) == 1:
        try:
            index = int(args[0])
        except ValueError:
            await stop_games.send("房间索引号应为整数")
        if index < 0 or index >= len(group_data["games"]):
            await stop_games.send("房间索引号超出范围，请使用 查车 查看有效的索引号")
        data_manager.remove_game_by_index(group_id, index)
        await stop_games.send(f"已关闭索引号为 {index} 的房间")
    elif len(args) == 2:
        game_name = args[0]
        
        game = data_manager.search_game(game_name)
        if not game:
            await stop_games.send(f"未找到游戏名称为 {game_name} 的游戏，请检查名称是否正确")
            return None

        game_id = game["game_id"]
        room_id = args[1]
        if not data_manager.check_game_exists(group_id, game_id, room_id):
            await stop_games.send("未找到指定的游戏房间，请检查游戏ID和房间ID是否正确")
        data_manager.remove_game_from_group(group_id, game_id, room_id)
        await stop_games.send(f"已关闭游戏ID为 {game_id}，房间ID为 {room_id} 的房间")
    else:
        await stop_games.send("参数错误，请提供正确的游戏ID和房间ID")
    
    return None
        