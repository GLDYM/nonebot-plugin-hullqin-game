import asyncio
import json
import random
import re
import time
from typing import Dict, List, Union, Optional
import aiohttp
from urllib.parse import urljoin

from nonebot import logger
from ..config import config
from .room_ws_fetcher import fetch_room_data

ua =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
HOME_URL = "https://game.hullqin.cn/"
RULE_PREFIX = "https://mp.weixin.qq.com/s/"
ROOM_ID_ALPHA = "qwertyupasdfghjkzxcvbnm"
ROOM_ID_MIXED = "qwert0yu1pa2sd3fg4hj5kz6xc7vb8nm9"

class GameScraper:
    def __init__(self) -> None:
        self._game_name_map: Dict[str, str] | None = None
        self._game_rule_map: Dict[str, str] | None = None
        

    async def _http_get_text(self, url: str, timeout: int = 15) -> str:
        request_timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=request_timeout, headers={"User-Agent": ua}) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.text(encoding="utf-8", errors="ignore")

    async def _fetch_frontend_maps(self) -> tuple[Dict[str, str], Dict[str, str]]:
        if self._game_name_map is not None and self._game_rule_map is not None:
            return self._game_name_map, self._game_rule_map

        home = await self._http_get_text(HOME_URL)
        app_match = re.search(r'"(https://[^\"]*?/app\.[^\"]+?\.chunk\.js)"', home)
        index_match = re.search(r'"(https://[^\"]*?/index\.[^\"]+?\.chunk\.js)"', home)
        if not app_match or not index_match:
            raise ValueError("未找到前端 chunk 地址")

        app_url = urljoin(HOME_URL, app_match.group(1))
        index_url = urljoin(HOME_URL, index_match.group(1))
        app_js, index_js = await asyncio.gather(
            self._http_get_text(app_url),
            self._http_get_text(index_url),
        )

        map_match = re.search(r'r=(\{.*?\}),o=', app_js)
        if not map_match:
            raise ValueError("未找到游戏映射")

        raw_map = map_match.group(1)
        json_map = re.sub(r'([,{])([a-z0-9]+):', r'\1"\2":', raw_map)
        name_map: Dict[str, str] = json.loads(json_map)

        rule_map: Dict[str, str] = {}
        for game_id, token in re.findall(r'gameKey:"([a-z0-9]+)",rule:""\.concat\(z,"([^\"]+)"\)', index_js):
            rule_map[game_id] = f"{RULE_PREFIX}{token}"

        self._game_name_map = name_map
        self._game_rule_map = rule_map
        return name_map, rule_map

    async def get_games_data(self) -> Dict[str, Union[int, List[Dict[str, str]]]]:
        logger.info("尝试获取游戏列表（优先 HTTP 解析）")
        expired_time = int(time.time()) + 86400 * 7
        games = {"expired_time": expired_time, "games": []}
        name_map, rule_map = await self._fetch_frontend_maps()
        for game_id, game_name in name_map.items():
            if not game_id or game_id == "p":
                continue
            games["games"].append(
                {
                    "game_name": game_name.strip(),
                    "game_id": game_id,
                    "rule_link": rule_map.get(game_id, "无"),
                }
            )

        logger.info(f"HTTP 解析获取到 {len(games['games'])} 个游戏")
        return games
    
    async def get_game_help(self, game_id: str) -> str:
        """获取游戏规则链接"""
        _, rule_map = await self._fetch_frontend_maps()
        return rule_map.get(game_id, "无")
    
    async def get_game_data(self, game_id: str, room_id: Optional[str] = None) -> Dict[str, str]:
        """获取房间"""
        expired_time = int(time.time()) + config.room_expired_time
        if room_id:
            return {"expired_time": expired_time, "room_id": room_id}

        def _pick_alpha() -> str:
            return ROOM_ID_ALPHA[random.randrange(len(ROOM_ID_ALPHA))]

        def _pick_digit() -> str:
            return str(random.randrange(10))

        v = random.randrange(3)
        generated_room_id = (
            _pick_alpha()
            + (_pick_alpha() if v else _pick_digit())
            + (ROOM_ID_MIXED[random.randrange(len(ROOM_ID_MIXED))] if v else _pick_digit())
            + _pick_digit()
        )
        logger.debug(f"为 {game_id} 生成房间号: {generated_room_id}")
        return {"expired_time": expired_time, "room_id": generated_room_id}

    async def get_room_data(self, game_id: str, room_id: str) -> Optional[Dict[str, Union[int, List[str]]]]:
        gid = "rBE" + "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(17)) + "g=="
        ws_data = await fetch_room_data(game_id=game_id, room_id=room_id, cookie_value=gid)
        if ws_data is not None:
            return ws_data
        else:
            logger.warning(f"未能获取到 {game_id} 房间 {room_id} 的数据")
            return None

game_scraper = GameScraper()