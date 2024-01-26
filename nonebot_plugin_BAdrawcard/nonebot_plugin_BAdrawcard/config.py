from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):
    proxy: Optional[str] = None  
    redis_host: str = "localhost"
    redis_port: int = 6379
    


    