from functools import wraps
import time
from typing import List, Tuple, Dict, TypeAlias
import asyncio

from nonebot import get_driver
from nonebot.log import logger
from httpx import AsyncClient, Response


from .utils import save_icon
from .config import Config


driver = get_driver()
plugin_config = Config.parse_obj(driver.config)

SCHALE_STUDENT_DETAILS_URL = "https://schale.gg/data/cn/students.min.json"
SCHALE_UPS_URL = "https://schale.gg/data/config.min.json"
PROXY = plugin_config.proxy

Adaptions: TypeAlias = List[int]
details: TypeAlias = Tuple[int, int, int, Adaptions]


def retry(tries: int = 4, delay: int = 3):
    def deco_retry(f):
        @wraps(f)
        def f_retry(url, **kwargs):
            mtries, mdelay = tries, delay

            while mtries > 1:
                try:
                    return f(url, **kwargs)
                except Exception:
                    logger.warning(
                        f"第{mtries}尝试请求{url}失败, 将在{mdelay}后重试"
                    )

                    time.sleep(mdelay)

                    mtries -= 1
                    mdelay *= 2
                    
            return f(url, **kwargs)

        return f_retry

    return deco_retry


@retry()
async def request_url(url: str, **kwargs) -> Response:
    async with AsyncClient(proxies=kwargs.get("proxy")) as _client:
        del kwargs["proxy"]
            
        return await _client.get(url, **kwargs)
    
    
class Schale_Spider:
    headers = {
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://schale.gg/?chara=Mina',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'v': '229',
    }

    @classmethod
    async def now_ups(cls) -> List[int]:
        res = await request_url(SCHALE_UPS_URL, proxy=PROXY)
        
        data = res.json()
        
        return data["Regions"][0]["CurrentGacha"][0]["characters"]
    
    
    @classmethod
    async def get_stundent_info(cls) -> Dict[str, details]:
        res = await request_url(SCHALE_STUDENT_DETAILS_URL, proxy=PROXY)
        
        data = res.json()
        
        return {
                student["Name"]: (
                student["Id"],
                student["IsLimited"],
                student["StarGrade"],
                [
                student["IndoorBattleAdaptation"],
                student["OutdoorBattleAdaptation"],
                student["StreetBattleAdaptation"]
                ]
            )   for student in data
        }
        
        
    @staticmethod
    async def download_icon(name: str, id: int) -> None:
        icon_url = f"https://schale.gg/images/student/collection/{id}.webp"

        res = await request_url(icon_url, proxy=PROXY)
        
        await save_icon(name, res.content)
        
        logger.success(f"[+]{name}的图标已经保存到studnet_icons目录!")
        
        
    @classmethod
    async def download_all_icons(cls) -> None:
        infos = {
            name: id
            for name, (id, *_) in (await cls.get_stundent_info()).items()
        }
        
        tasks = [
            cls.download_icon(name, id)
            for name, id in infos.items()
        ]
        
        await asyncio.gather(*tasks)
       
