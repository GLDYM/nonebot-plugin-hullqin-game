import re
import shlex

from typing import List, Dict, Union

from nonebot import on_command, logger
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


open_games = on_command(
    "open_games",
    aliases={"发车", "开房", "开房间"},
    priority=5,
    force_whitespace=True,
    block=True,
)


@open_games.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = event.group_id
    args = shlex.split(arg.extract_plain_text())
    logger.info(f"{group_id} 发车参数: {args}")

    games_list = await data_manager.get_games_list()
    data_manager.remove_expired_games(group_id)

    if not args or args == []:
        message_lines = ["==== 游戏列表 ===="]
        for game in games_list:
            game_name = game.get("game_name")
            game_id = game.get("game_id")
            message_lines.append(f"{game_name}（游戏ID: {game_id}）")
        await forward_send(bot, event, [MessageSegment.text("\n".join(message_lines))])
        return None

    match len(args):
        case 1:
            game_name = args[0]
            room_id = None
        case 2:
            game_name, room_id = args
            if not bool(re.match(r"^[a-z0-9]{4}$", room_id)):
                await open_games.send("房间ID格式错误，应为4位小写字母或数字组合。")
                return None
            if data_manager.check_game_exists(group_id, game_name, room_id):
                await open_games.send("这个房间在这个群有了！请输入 查房 查看房间列表")
                return None
            await open_games.send("⚠️你指定了房间ID，不保证房间一定未占用")
        case _:
            await open_games.send("参数错误，请使用：发车 [游戏名称]")
            return None

    game = data_manager.search_game(game_name)

    if game is None:
        await open_games.send("未找到该游戏，请输入 发车 查看可用游戏。")
        return None

    game_name = game.get("game_name")
    game_id = game.get("game_id")
    rule_link = game.get("rule_link", "无")

    game_data = await game_scraper.get_game_data(game_id, room_id)

    expired_time = game_data.get("expired_time")
    room_id = game_data["room_id"]

    data_manager.add_game_to_group(
        group_id,
        {
            "expired_time": expired_time,
            "game_name": game_name,
            "game_id": game_id,
            "room_id": room_id,
            "rule_link": rule_link,
        },
    )
    message = await create_game_message(
        game["game_name"],
        game["game_id"],
        room_id,
        rule_link,
    )

    await open_games.send(message)
    return None

async def create_game_message(
    game_name: str,
    game_id: str,
    room_id: str,
    rule_link: str,
) -> MessageSegment:
    game_link = f"https://game.hullqin.cn/{game_id}/{room_id}"
    message = (
        f"🎉 桌游发车成功！ 🎉\n\n"
        f"游戏名称：{game_name}\n"
        f"房间链接：{game_link}\n"
        f"规则链接：{rule_link}"
    )
    return MessageSegment.text(message)


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
