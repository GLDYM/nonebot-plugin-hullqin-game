# -*- coding: utf-8 -*-
"""
本模块负责插件的数据管理，包括文件路径管理和用户数据的加载与保存。
hullqin_game/
├── games_data.json # {"expired_time": 1769480810, "games": [{"game_name": "UNO", "game_id": "uno", "rule_link": "https://..."}, ...]}
├── <group_id>.json # {"games": [{"expired_time": 1769480810, "game_name": "UNO", "game_id": "uno", "room_id": zmqq, "rule_link": "https://..."}, ...]}
└── ...
"""
import json
import time

from pathlib import Path
from typing import Dict, List, Union

import nonebot_plugin_localstore as store

from .game_scraper import game_scraper

class DataManager:
    def __init__(self):
        self.data_path: Path = Path(store.get_plugin_config_dir())
        self.games_data_path: Path = self.data_path / "games_data.json"
        self._init_data()

    def _init_data(self):
        self.data_path.mkdir(parents=True, exist_ok=True)
        if not self.games_data_path.exists():
            with open(self.games_data_path, "w", encoding="utf-8") as file:
                json.dump({"expired_time": 0, "games": []}, file, ensure_ascii=False, indent=4)

    
    def load_games_data(self) -> Dict[str, Union[int, List[Dict[str, str]]]]:
        """加载游戏数据"""
        try:
            with open(self.games_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"expired_time": 0, "games": []}
        
    def save_games_data(self, games_data: Dict[str, Union[int, List[Dict[str, str]]]]):
        """保存游戏列表数据"""
        with open(self.games_data_path, "w", encoding="utf-8") as f:
            json.dump(games_data, f, ensure_ascii=False, indent=4)
    
    def reset_games_data(self):
        """重置游戏列表数据"""
        with open(self.games_data_path, "w", encoding="utf-8") as f:
            json.dump({"expired_time": 0, "games": []}, f, ensure_ascii=False, indent=4)
        
    def search_game(self, game_name: str) -> Union[Dict[str, str], None]:
        """在游戏数据中搜索游戏"""
        games_data = self.load_games_data()
        for game in games_data.get("games", []):
            if game["game_id"] == game_name or game["game_name"] == game_name:
                return game
        return None

    async def get_games_list(self) -> Dict[str, Union[int, List[Dict[str, str]]]]:
        """获取游戏列表"""
        games_data = self.load_games_data()
        if games_data and int(time.time()) < games_data.get("expired_time", 0):
            return games_data.get("games", [])
        else:
            games_data = await game_scraper.get_games_data()
            self.save_games_data(games_data)
            return games_data.get("games", [])


    def get_group_file_path(self, group_id: int) -> Path:
        """获取群组的数据文件路径"""
        return self.data_path / f"{group_id}.json"

    def load_group_data(self, group_id: int) -> Dict[str, List[Dict[str, any]]]:
        """加载数据"""
        try:
            with open(self.get_group_file_path(group_id), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"games": []}

    def save_group_data(self, group_id: int, group_data: Dict[str, List[Dict[str, any]]]):
        """保存数据"""
        with open(self.get_group_file_path(group_id), "w", encoding="utf-8") as f:
            json.dump(group_data, f, ensure_ascii=False, indent=4)
            
    def reset_group_data(self, group_id: int):
        """重置群组数据"""
        group_id = str(group_id)
        with open(self.get_group_file_path(group_id), "w", encoding="utf-8") as f:
            json.dump({"games": []}, f, ensure_ascii=False, indent=4)

    def add_game_to_group(self, group_id: int, game_data: Dict):
        """将游戏加入本群列表"""
        group_data = self.load_group_data(group_id)
        group_id = str(group_id)
        if "games" not in group_data:
            group_data["games"] = []
        group_data["games"].append(game_data)
        self.save_group_data(group_id, group_data)
    
    def remove_game_from_group(self, group_id: int, game_id: str, room_id: str):
        """将游戏从本群列表中移除，通过ID定位"""
        group_data = self.load_group_data(group_id)
        group_id = str(group_id)
        if "games" not in group_data:
            group_data["games"] = []
        for game in group_data["games"]:
            if game["game_id"] == game_id and game["room_id"] == room_id:
                group_data["games"].remove(game)
                break
        self.save_group_data(group_id, group_data)
        
    def remove_game_by_index(self, group_id: int, index: int):
        """将游戏从本群列表中移除，通过索引定位"""
        group_data = self.load_group_data(group_id)
        group_id = str(group_id)
        if "games" not in group_data:
            group_data["games"] = []
        if 0 <= index < len(group_data["games"]):
            group_data["games"].pop(index)
        self.save_group_data(group_id, group_data)

    def check_game_exists(self, group_id: int, game_id: str, room_id: str) -> bool:
        """检查游戏是否存在于本群列表中"""
        group_data = self.load_group_data(group_id)
        if "games" not in group_data:
            group_data["games"] = []
            return False
        for game in group_data["games"]:
            if game["game_id"] == game_id and game["room_id"] == room_id:
                return True
        return False

    def remove_expired_games(self, group_id: int):
        """移除过期的游戏"""
        group_data = self.load_group_data(group_id)
        group_id = str(group_id)
        if "games" not in group_data:
            group_data["games"] = []
        group_data["games"] = [
            game for game in group_data["games"]
            if int(time.time()) < game["expired_time"]
        ]
        self.save_group_data(group_id, group_data)


data_manager = DataManager()
