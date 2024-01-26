from typing import Any, List, Dict

from nonebot.log import logger

from .models import Student, probability, pool


FES = {
    "star3_fes": 300,
    "special": 70
}

NOT_FES = {
    "star3_fes": 0,
    "special": 0
}


def on_fes() -> None:
    probability.re_assign(FES)
    logger.info("已开启fes")


def off_fes() -> None:
    probability.re_assign(NOT_FES)
    logger.info("已关闭fes")


async def remove_old_ups() -> None:
    for name in (pool.up + pool.star2up):
        student = await Student.load(name)
        
        if student.isLimited == 1:
            pool.up.remove(student.name)
        elif student.rarity == 3 and sum(student.adaption) == 7:
            pool.up.remove(student.name)
            pool.special.append(student.name)
            off_fes()
        elif student.rarity == 3:
            pool.up.remove(student.name)
            pool.star3.append(student.name)
        elif student.rarity == 2:
            pool.star2up.remove(student.name)
            pool.star2.append(student.name)
            probability.star2up = 0
        
        await student.remove()
        logger.success(f"[+]{name}已被移除出UP池")
        

async def add_new_ups(infos: List[Dict[str, Any]]) -> None:
    for info in infos:
        student = Student(**info)
        
        if student.isLimited == 1:
            pool.up.append(student.name)
        elif student.rarity == 3 and sum(student.adaption) == 7 :
            pool.up.append(student.name)
            pool.special.remove(student.name)
            on_fes()
        elif student.rarity == 3:
            pool.up.append(student.name)
            pool.star3.remove(student.name)          
        elif student.rarity == 2:
            pool.star2up.append(student.name)
            pool.star2.remove(student.name) 
            probability.star2up = 300
        
        await student.dump()
        logger.success(f"[+]{student.name}已添加到UP池")

    




    