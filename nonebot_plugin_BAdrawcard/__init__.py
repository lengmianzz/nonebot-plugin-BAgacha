from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot import require

require("nonebot_plugin_saa")

from .config import Config


__plugin_meta__ = PluginMetadata(
    name="BA模拟抽卡",
    description="模拟实现了碧蓝档案游戏的抽卡功能, 自动化了更新卡池、FES提高卡池概率",
    usage=("/ba单抽\n"
           "/ba十连\n"
           "/ba来一井\n"
           "/当前up\n"
           "/当前概率\n"
           ),

    type="application",

    homepage="https://github.com/lengmianzz/nonebot-plugin-BAdrawcard",

    config=Config,

    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
)