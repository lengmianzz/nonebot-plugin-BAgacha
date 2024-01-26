import asyncio
import abc
from typing import List, Tuple, Dict, Any
from typing_extensions import Self
import json

from pydantic import BaseModel, Json
from nonebot.log import logger
from nonebot import get_driver

from .spider import Schale_Spider
from .db import db


driver = get_driver()


class HashModel(BaseModel, abc.ABC):    
    _client = db._client

    @classmethod
    @abc.abstractmethod
    async def load(cls) -> Any:
        raise NotImplementedError


    @abc.abstractmethod
    async def dump(self) -> Any:
        raise NotImplementedError
    
    
    def re_assign(self, data: Dict[str, Any]) -> None:
        for field, value in data.items():
            setattr(self, field, json.loads(value))
    

class Pool(HashModel):
    up: Json[List[str]]
    star3: Json[List[str]]
    star2up: Json[List[str]]
    star2: Json[List[str]]
    star1: Json[List[str]]
    special: Json[List[str]]
    
    @property
    def pool_names(self) -> Tuple[str, ...]:
        return tuple(self.__fields__.keys())
    
    
    def get(self, pool_name: str) -> Any:
        return self.__getattribute__(pool_name)
    
    
    @classmethod
    async def load(cls) -> Self:
        if cls._client.exists(field_name := cls.__name__.lower()):
            data = {key: value
                    for key, value in (
                        cls._client.hgetall(field_name).items()
                    )
                }         
        else:
            data = await cls.init()
        
        return cls.parse_obj(data)
    
    
    async def dump(self) -> None:
        dct = {k: json.dumps(v)
            for k, v in self.dict().items()
        }
        
        self._client.hmset(type(self).__name__.lower(), dct) # type: ignore
        
        logger.success("[+]已保存卡池模型到数据库")
    
    
    @classmethod
    async def init(cls) -> Dict[str, str]:
        tobe_parsed_dct = {
            k: list() for k in cls.__fields__.keys()
        }
        
        info_mapping = {
            (1, 0, 6): "star1",
            (2, 'in up', 7): "star2up",
            (2, 0, 7): "star2",
            (2, 0, 6): "star2",
            (3, 'in up', 6): "up",
            (3, 1, 7): "special",
            (3, 0, 6): "star3"
        }
        
        infos = await Schale_Spider.get_stundent_info()
        now_ups = await Schale_Spider.now_ups()

        for name, detail in infos.items():
            ID, isLimited, star, adaption = detail[0], detail[1], detail[2], detail[3]
            
            if condition := (
                    info_mapping.get(
                        (star, 'in up' if ID in now_ups else isLimited, sum(adaption)), #type: ignore
                        None
                    )
                ):  
                tobe_parsed_dct[condition].append(name)
                
            if condition and "up" in condition: # info_mapping有一种情况没列入, 会导致condition为None
                dct = {
                    "name": name,
                    "id": ID,
                    "isLimited": isLimited,
                    "rarity": star,   
                    "adaption": json.dumps(adaption)
                }
                
                student = Student(**dct)
                await student.dump()
                
        return {k: json.dumps(v) for k, v in tobe_parsed_dct.items()}


class Probability(HashModel):
    up: int
    star3: int 
    star2: int 
    star1: int 
    star3_fes: int
    star2up: int 
    special: int
    
    @property
    def weights(self) -> List[int]:
        return [
            self.up,
            
            self.star3 + self.star3_fes,
            
            self.star2up,
            
            self.star2,
            
            self.star1 - self.star3_fes - self.star2up - self.special,
            
            self.special
        ]

    
    @classmethod
    async def load(cls) -> Self:
        if cls._client.exists(field_name := cls.__name__.lower()):
            data = cls._client.hgetall(field_name)
        else:
            data = await cls.init()
        
        return cls.parse_obj(data)
            
            
    async def dump(self) -> None:
        dct = {
            key: value
            for key, value in self.dict().items()
        }
        
        self._client.hmset(type(self).__name__.lower(), dct) #type: ignore
        logger.success("[+]已保存概率模型到数据库")
    
    
    @classmethod
    async def init(cls) -> Dict[str, int]:
        return {
            "up": 70,
            "star3": 230,
            "star2": 1850,
            "star1": 7850,
            "star3_fes": 0,
            "star2up": 0,
            "special": 0
            }


class Student(HashModel):
    name: str
    id: int
    isLimited: int
    rarity: int
    adaption: Json[List[int]]

    @classmethod
    async def load(cls, name: str) -> Self:
        try:
            data = cls._client.hgetall(name.title())
            return cls.parse_obj(data)
        except:
            logger.error("数据库不存在该学生")
            raise
        
        
    async def dump(self) -> None:
        data = {key: json.dumps(value) if isinstance(value, list) else value
                for key, value in self.dict().items()
        }
        self._client.hmset(self.name.title(), data) #type: ignore
        
        logger.success(f"[+]已保存{self.name}模型!")
        
    
    async def remove(self) -> None:
        if self._client.exists(self.name.title()):
            self._client.delete(self.name.title())
            
            logger.success(f"[+]已删除{self.name}模型")
        
     
@driver.on_shutdown
async def save_models() -> None:
    global pool, probability
    
    await pool.dump()
    await probability.dump()
        

pool = asyncio.run(Pool.load())
probability = asyncio.run(Probability.load())
