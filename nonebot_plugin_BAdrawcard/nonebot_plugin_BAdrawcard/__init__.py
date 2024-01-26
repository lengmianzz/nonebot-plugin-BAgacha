from nonebot.plugin import PluginMetadata

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

    homepage="{项目主页}",

    config=Config,

    supported_adapters={"~onebot.v11", },
)