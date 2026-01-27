import time
from typing import Dict, List, Union, Optional

from nonebot import logger, get_driver
from playwright.async_api import Browser, Error, Playwright, async_playwright

from ..config import config
from .install_browser import install_browser

ua =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"

class GameScraper:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
    
    async def init_browser(self, **kwargs) -> None:
        """初始化浏览器"""
        self.playwright = await async_playwright().start()
        try:
            self.browser = await self.launch_browser(**kwargs)
        except Error:
            await install_browser()
            self.browser = await self.launch_browser(**kwargs)
        return self.browser
    
    async def launch_browser(self, **kwargs) -> Browser:
        assert self.playwright is not None, "Playwright 没有安装"
        logger.info("使用 chromium 启动")
        return await self.playwright.chromium.launch(headless=config.playwright_headless, **kwargs)


    async def get_games_data(self) -> Dict[str, Union[int, List[Dict[str, str]]]]:
        assert self.browser is not None, "浏览器未初始化"
        logger.info("尝试获取游戏列表")
        page = await self.browser.new_page(user_agent=ua)
        
        page.set_default_timeout(30000)  # 设置默认超时时间为30秒
        
        await page.goto("https://game.hullqin.cn/")

        await page.wait_for_load_state("networkidle")

        items = await page.query_selector_all(".justify-center a")

        expired_time = int(time.time()) + 86400 * 7
        games = {"expired_time": expired_time, "games": []}

        for item in items:
            href = await item.get_attribute("href")   # 游戏 id
            text = await item.inner_text()            # 游戏名称
            games["games"].append({"game_name": text.strip(), "game_id": href.replace("/", "")})

        await page.close()

        logger.info(f"获取到 {len(games['games'])} 个游戏")

        for game in games["games"]:
            rule_link = await self.get_game_help(game["game_id"])
            game["rule_link"] = rule_link

        return games.get("games", [])
    
    async def get_game_help(self, game_id: str) -> str:
        """获取游戏规则链接"""
        assert self.browser is not None, "浏览器未初始化"
        logger.info(f"尝试获取{game_id}游戏规则链接")
        page = await self.browser.new_page(user_agent=ua)
        
        page.set_default_timeout(30000)  # 设置默认超时时间为30秒
        
        await page.goto(f"https://game.hullqin.cn/{game_id}", timeout=30000)

        await page.wait_for_load_state("networkidle", timeout=30000)
        
        # 提取规则链接（查找包含 "查看规则" 的按钮） 
        rule_link = await page.query_selector("a:text('查看规则')") 
        rule = "无"
        if rule_link: 
            rule = await rule_link.get_attribute("href") 
        
        await page.close()
        
        return rule
    
    async def get_game_data(self, game_id: str, room_id: Optional[str] = None) -> Dict[str, str]:
        """获取房间"""
        expired_time = int(time.time()) + config.room_expired_time
        if room_id:
            return {"expired_time": expired_time, "room_id": room_id}
        
        assert self.browser is not None, "浏览器未初始化"
        page = await self.browser.new_page(user_agent=ua)
        
        page.set_default_timeout(30000)  # 设置默认超时时间为30秒
        
        await page.goto(f"https://game.hullqin.cn/{game_id}", timeout=30000)

        await page.wait_for_load_state("networkidle", timeout=30000)

        if room_id is None:
            room_link = await page.query_selector(f"a[href^='/{game_id}/']") 
            if room_link: 
                room_href = await room_link.get_attribute("href") 
                room_id = room_href.split("/")[-1]
        
        await page.close()
        
        return {"expired_time": expired_time, "room_id": room_id}

    async def get_room_data(self, game_id: str, room_id: str) -> Optional[Dict[str, Union[int, List[str]]]]:
        url = f"https://game.hullqin.cn/{game_id}/{room_id}"
        
        page = await self.browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        # 检查是否有 "观战中"
        content = await page.content()
        if "观战中" not in content:
            await page.close()
            return None

        players = []
        seat_index = 0

        while True:
            seat = await page.query_selector(f"#userseat{seat_index}")
            if not seat:
                break
            player_div = await seat.query_selector("div.text-2xl.overflow-hidden")
            if player_div:
                name = await player_div.inner_text()
                players.append(name.strip())
            else:
                player_head = await seat.query_selector("div.head-image")
                if player_head:
                    players.append("神秘人")
            seat_index += 1

        await page.close()

        current = len(players)
        total = seat_index
        return {
            "current": current,
            "total": total,
            "players": players
        }

game_scraper = GameScraper()
driver = get_driver()

@driver.on_startup
async def init_card() -> None:
    await game_scraper.init_browser()