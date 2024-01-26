from typing import Tuple, List
from collections import Counter
import random

from PIL import Image

from .draw import Draw
from .utils import open_icon, open_pic
from .models import pool, probability


class Pull:
    @staticmethod
    def _generate_every_pool_pulls(times: int) -> Counter[str]:
        return Counter(
            random.choices(pool.pool_names, weights=probability.weights, k=times)
        )

    @staticmethod
    def minimum(names: List[str]) -> List[str]:
        """10连的保底机制, 在抽到10蓝时用魔法转变为9蓝一金"""
        return names[:9] + random.choices(pool.get("star2"))

    @classmethod
    def pulls(
        cls, numbers_of_every_pool: Counter[str], *, only_star3: bool = False
    ) -> List[str]:
        pool_names = pool.pool_names[:2] if only_star3 else pool.pool_names

        return [
            name
            for pool_name in pool_names
            for name in random.choices(
                pool.get(pool_name), k=numbers_of_every_pool[pool_name]
            )
        ]

    @classmethod
    async def one_pulls(cls) -> Tuple[List[str], Image.Image]:
        counter = cls._generate_every_pool_pulls(1)

        name = (cls.pulls(counter))[0]
        msg = [f"Sensei抽到的是{name}哦~"]
        img = await open_icon(name)
        return msg, img

    @classmethod
    async def ten_pulls(cls) -> Tuple[List[str], Image.Image]:
        counter = cls._generate_every_pool_pulls(10)
        names = cls.pulls(counter)

        msg = [
            f"Sensei一共抽到了{counter['up']}个up学生,",
            f"{counter['star3']}个3星学生,",
            f"{counter['special']}个special学生," if counter["special"] else "",
            f"{counter['star2up']}个2星up学生," if counter["star2up"] else "",
            f"{counter['star2']}个2星学生,",
            f"{counter['star1']}个1星学生.",
        ]

        if set(names).issubset(set(pool.get("star1"))):
            names = Pull.minimum(names)

        img = await Draw.embed_into_background(names, small=False)
        return msg, img

    @classmethod
    async def two_hundred_pulls(cls) -> Tuple[List[str], Image.Image]:
        counter = cls._generate_every_pool_pulls(200)
        names = cls.pulls(counter, only_star3=True)

        msg = [
            f"Sensei一共抽到了{counter['up']}个up学生,",
            f"{counter['star3']}个3星学生,",
            f"{counter['special']}个special学生," if counter["special"] else "",
            f"{counter['star2up']}个2星up学生," if counter["star2up"] else "",
            f"{counter['star2']}个2星学生,",
            f"{counter['star1']}个1星学生.",
        ]

        if counter.get("star3") or counter.get("up"):
            result_pic = await Draw.embed_into_background(names, small=True)
        else:
            result_pic = await open_pic("ji.jpg")

        return msg, result_pic


