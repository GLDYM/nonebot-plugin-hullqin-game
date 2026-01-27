<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

# Hullqin Game 桌游发车

_✨ 快速创建 https://game.hullqin.cn/ 房间并招募玩家 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/GLDYM/nonebot-plugin-hullqin-game.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-hullqin-game">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-hullqin-game.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## ✨ 功能特性

- 快速创建 [Hullqin game](https://game.hullqin.cn/) 指定游戏的房间
- 快速查询当前群内招募的桌游

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-hullqin-game

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-hullqin-game
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-hullqin-game
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-hullqin-game
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-hullqin-game
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_hullqin_game"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置

| 配置项              | 必填 | 说明                                    |
|:-------------------:|:----:|:---------------------------------------:|
| room_expired_time   | 否   | 招募的过期时间，默认为20min（1200）。   |
| playwright_headless | 否   | Playwright 是否无头模式，调试用。       |

## 📝 命令列表

| 命令                 | 功能描述                                         |
| :------------------- | :----------------------------------------------- |
| `发车 [game] [room]` | 发起新的桌游招募信息，不填游戏名显示游戏列表     |
| `查车`               | 查看本群的桌游招募信息                           |

## 🤝 贡献

欢迎提交 Pull Request 或 Issue 来改进这个插件！

## 特别感谢

- [Hullqin game](https://game.hullqin.cn/)