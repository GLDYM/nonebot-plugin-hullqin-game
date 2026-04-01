import asyncio
from typing import Dict, List, Optional, Union

from .ws_pb2 import WsData


def _decode_room(binary_data: bytes) -> Optional[Dict[str, Union[int, List[str]]]]:
    msg = WsData()
    msg.ParseFromString(binary_data)
    if not msg.room:
        return None

    players: List[str] = []
    total = len(msg.room.playerList)
    for player in msg.room.playerList:
        name = player.name.strip() if player.name else ""
        emoji = bytes(player.emoji).decode("utf-8", errors="ignore").strip() if player.emoji else ""

        # 登录用户用 name，匿名用户用 emoji；两者都空视为空位。
        if not (name or emoji):
            continue

        if name:
            players.append(name)
        else:
            players.append(emoji)

    current = len(players)
    return {
        "current": current,
        "total": total,
        "players": players,
    }


async def fetch_room_data(
    game_id: str,
    room_id: str,
    cookie_value: str,
) -> Optional[Dict[str, Union[int, List[str]]]]:
    import websocket

    ws_url = f"wss://game.hullqin.cn/{game_id}/{room_id}?v=1"
    holder: dict[str, Optional[Dict[str, Union[int, List[str]]]]] = {"result": None}
    done = asyncio.Event()

    def _on_open(_ws):
        return None

    def _on_message(ws, message):
        if isinstance(message, bytes):
            data = _decode_room(message)
            if data is not None:
                holder["result"] = data
                done.set()
                ws.close()

    def _on_error(_ws, _err):
        done.set()

    def _on_close(_ws, _code, _msg):
        done.set()

    ws = websocket.WebSocketApp(
        ws_url,
        header=[
            "Origin: https://game.hullqin.cn",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
            f"Cookie: gid={cookie_value}",
        ],
        on_open=_on_open,
        on_message=_on_message,
        on_error=_on_error,
        on_close=_on_close,
    )

    thread_task = asyncio.to_thread(ws.run_forever)
    runner = asyncio.create_task(thread_task)
    try:
        await done.wait()
    finally:
        ws.close()
        await runner

    return holder["result"]
