import redis
from redis.exceptions import ConnectionError
from nonebot import get_driver
from nonebot.log import logger

from .config import Config


driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


class DB:
    _clinet = None
    
    @classmethod
    def get__client(cls) -> redis.Redis:
        try:
            cls._clinet = redis.StrictRedis(
                host=plugin_config.redis_host,
                port=plugin_config.redis_port,
                decode_responses=True,
                charset='UTF-8'
            )
        except ConnectionError:
            logger.error("与Redis连接失败")
            raise
        
        return cls._clinet
    
    
    async def close_db(self) -> None:
        if self._client:
            self._client.close()
    
    
    @property
    def _client(self) -> redis.Redis:
        return self._clinet if self._clinet else self.get__client()

    
    
db = DB()
        

