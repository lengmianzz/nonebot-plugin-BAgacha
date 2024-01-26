from typing import NoReturn
import asyncio
from datetime import datetime
import json

from nonebot.log import logger
from nonebot import require, on_command, get_driver, get_adapters, get_bot
from nonebot.permission import SUPERUSER 
from nonebot.adapters import Event
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_saa")
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import (
    MessageFactory,
    Text, Image,
    enable_auto_select_bot,
    extract_target,
    PlatformTarget
)
enable_auto_select_bot()

from .pull import Pull
from .models import pool, probability
from .utils import (
    create_msg,
    image2byte,
    load_cd,
    clear_cd,
    icon_is_empty,
    load_white,
    save_cd,
    save_white,
    stored_icon_names
)
from .manage import remove_old_ups, add_new_ups
from .draw import embed_ups
from .db import db
from .spider import Schale_Spider
from .models import Student


START_DATE = datetime(2024, 1, 17, 13, 0, 0)

driver = get_driver()
adapters = get_adapters()

matcher0 = on_command("ba单抽", block=True)
matcher1 = on_command("ba十连", block=True)
matcher2 = on_command("ba来一井", block=True)
matcher3 = on_command("抽卡概率", aliases={"当前概率", "显示概率"}, block=True)
matcher4 = on_command("当前up", aliases={"当前up学生"}, block=True)

cd =  asyncio.run(load_cd())
white = asyncio.run(load_white())


@matcher0.handle()
async def send_one_pulls_res(event: Event) -> NoReturn:
    word, img = await Pull.one_pulls()
    pic = image2byte(img)
    
    msg = create_msg(pic, event.get_user_id(), word)

    await msg.send()
    await matcher0.finish()


@matcher1.handle()
async def send_ten_pulls_res(event: Event) -> NoReturn:
    words, img = await Pull.ten_pulls()
    
    pic = image2byte(img)
    
    msg = create_msg(pic, event.get_user_id(), words)

    await msg.send()
    await matcher1.finish()
    
    
@matcher2.handle()
async def send_two_hundred_pulls_res(event: Event) -> NoReturn:
    user_id = event.get_user_id()
    cd[user_id] = cd.get(user_id, 0)
        
    if cd.get(user_id, 0) < 3:
        cd[user_id] += 1
        
        words, img = await Pull.two_hundred_pulls()
    
        pic = image2byte(img)
        
        msg = create_msg(pic, event.get_user_id(), words)

        await msg.send()
        await matcher2.finish()
    else:
        await MessageFactory("对不起, Sensei每天只能抽3井哦~").send()
        await matcher2.finish()


@matcher3.handle()
async def send_probability() -> NoReturn:
    stars = ("up", "3星", "2星up", "2星", "1星", "fes")
    
    msg = MessageFactory(
        [
            Text(f"当前{star}学生的概率为: {p / 100}%\n")
            for star, p in zip(stars, probability.weights)
            if p != 0
        ]
    )
    
    await msg.send()
    await matcher3.finish()
    

@matcher4.handle()
async def send_now_ups() -> NoReturn:
    img = await embed_ups(pool.up + pool.star2up)

    msg = MessageFactory([Text("当前UP的学生是: \n"), Image(image2byte(img))])
    
    await msg.send(at_sender=True)
    await matcher4.finish()
    
    
@driver.on_bot_connect
async def _() -> None:
    bot = get_bot()
    
    if bot.adapter.get_name() == "OneBot V11":
        from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER
        
        matcher5 = on_command("订阅更新", block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
    else:
        matcher5 = on_command("订阅更新", block=True, permission=SUPERUSER)
        

    @matcher5.handle()
    async def _(event: Event) -> NoReturn:
        target = extract_target(event)
        white.append(target.json())
        
        msg = MessageFactory("订阅更新成功!")
        
        await msg.send(at_sender=True)
        await matcher5.finish()


@driver.on_startup
async def init_icons() -> NoReturn:
    if icon_is_empty():
        await Schale_Spider.download_all_icons()
        logger.success("[+]已添加全部学生图标到数据库")


@driver.on_startup
async def overtake_update() -> NoReturn:
    """
        如果当前数据库存储的up学生与Schale网站的最新up不同,
        则用Schale的数据重新初始化`Pool`模型,
        并下载缺失的图标.
        假如长期没使用本插件, 也能在重新启动本插件时自动更新, 立即使用.
    """
    up_students = [await Student.load(name) for name in (pool.up + pool.star2up)]
    up_ids = [student.id for student in up_students]
    latested_up_ids = await Schale_Spider.now_ups()
    
    if sorted(up_ids) != sorted(latested_up_ids):
        data = await pool.init()
        pool.re_assign(data)
        
        for student in up_students:
            logger.success(f"[+]{student.name}已被移除出up池")
            await student.remove()
        
    latested_infos = await Schale_Spider.get_stundent_info() 
        
        
    update_names = set(latested_infos.keys()) - stored_icon_names()
    
    update_infos = {name: ID
        for name in update_names
        for target_name, (ID, *_) in latested_infos.items()
        if name == target_name
    }

    if update_infos:
        tasks = [
            Schale_Spider.download_icon(name, ID)
            for name, ID in update_infos.items()
        ]
        
        await asyncio.gather(*tasks)
    
        logger.success("[+]已更新图标到最新进度")
        

@driver.on_shutdown
async def close_db() -> NoReturn:
    await db.close_db()
    
    logger.info("与数据库的连接已断开")


@driver.on_shutdown
async def dump_json() -> NoReturn:
    global cd, white
    
    await save_cd(cd)
    logger.info("已保存CD数据")
    
    await save_white(white)
    logger.info("已保存白名单")
    

@scheduler.scheduled_job("cron", hour=23)
async def aps_clear_cd() -> NoReturn:
    await clear_cd()
    
    logger.success("[+]已清除CD")
    
    
@scheduler.scheduled_job('interval', days=8, start_date=START_DATE)
async def latest_update() -> NoReturn:
    latested_up_ids = await Schale_Spider.now_ups()
    up_ids = [(await Student.load(name)).id for name in (pool.up + pool.star2up)]

    if sorted(up_ids) != sorted(latested_up_ids):
        await remove_old_ups()
        
        studnet_infos = await Schale_Spider.get_stundent_info()

        await add_new_ups(
            [
                {
                "name": name,
                "id": details[0],
                "isLimited": details[1],
                "rarity": details[2],
                "adaption": json.dumps(details[3])
                }
                for name, details in studnet_infos.items()
                if details[0] in latested_up_ids 
            ]
        )
        
        logger.success("[+]已更新up池!")
        
        if white:
            img = await embed_ups(pool.up + pool.star2up)
            
            msg = MessageFactory(
                [
                    Text("已自动更新up池, 当前的up学生是: \n"),
                    Image(image2byte(img))
                ]
                
            )
            
            for serialized_target in white:
                target = PlatformTarget.deserialize(serialized_target)
                await msg.send_to(target)
        
