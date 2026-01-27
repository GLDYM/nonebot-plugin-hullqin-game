import shlex
from typing import Dict, List, Union

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment,
)

from ..utils.data_manager import data_manager
from ..utils.game_scraper import game_scraper

query_games = on_command(
    "query_games", aliases={"查车", "查房", "房间列表"}, priority=5, block=True
)


@query_games.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = event.group_id
    args = shlex.split(arg.extract_plain_text())

    group_data = data_manager.load_group_data(group_id)
    if "games" not in group_data or not group_data["games"]:
        await query_games.send("当前没有任何桌游房间哦~")
        return None

    data_manager.remove_expired_games(group_id)

    if not group_data["games"]:
        await query_games.send("当前没有任何桌游房间哦~")
        return None

    if args and len(args) == 1:
        game_name = args[0]
        game_data = data_manager.search_game(game_name)
        filtered_games = [
            game for game in group_data["games"] if game["game_id"] == game_data["game_id"]
        ]
        if not filtered_games or filtered_games == []:
            await query_games.send(f"当前没有找到 {game_name} 的房间哦~")
            return None
        room_list = filtered_games
    else:
        room_list = group_data["games"]

    i = 0
    message_lines = ["==== 房间列表 ===="]
    for game in room_list:
        game_name = game.get("game_name")
        game_id = game.get("game_id")
        room_id = game.get("room_id")
        rule = game.get("rule_link", "无")
        url = f"https://game.hullqin.cn/{game_id}/{room_id}"
        
        """
        current = await game_scraper.get_room_data(game_id, room_id)
        if current:
            current_players = current["current"]
            total_players = current["total"]
            players = current["players"]
            player_list = "，".join(players)
            message_lines.append(
                f"{i}. {game_name}（{current_players}/{total_players}）：{url}\n> 规则链接: {rule}\n> 玩家列表: {player_list}"
            )
        else:
            message_lines.append(
                f"{i}. {game_name}：{url}\n> 规则链接: {rule}"
            )
        """
        message_lines.append(
            f"{i}. {game_name}：{url}\n> 规则链接: {rule}"
        )
        i += 1

    if len(message_lines) <= 5:
        await query_games.send("\n".join(message_lines))
    else:
        await forward_send(
            bot,
            event,
            [MessageSegment.text(message_line) for message_line in message_lines],
        )


async def forward_send(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    messages: List[MessageSegment],
) -> None:
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=[
                {
                    "type": "node",
                    "data": {
                        "name": "花花",
                        "uin": bot.self_id,
                        "content": msg,
                    },
                }
                for msg in messages
            ],
        )
    else:
        await bot.send_private_forward_msg(
            user_id=event.user_id,
            messages=[
                {
                    "type": "node",
                    "data": {
                        "name": "花花",
                        "uin": bot.self_id,
                        "content": msg,
                    },
                }
                for msg in messages
            ],
        )
