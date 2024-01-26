from typing import Dict, Union, List, Set, Tuple
from io import BytesIO
from pathlib import Path
import json
import os
import uuid

import aiofiles
from PIL import Image
from nonebot import require
require("nonebot_plugin_saa")
from nonebot_plugin_saa import MessageFactory, Image as saa_image , Mention, Text

DATA_PATH = Path(__file__).parent / "Data"
ICONS_PATH =  DATA_PATH / "student_icons"
CD_PATH = DATA_PATH / "cd.json"
WHITE_PATH = DATA_PATH / "white.json"


def image2byte(image: Image.Image) -> bytes:
    img_bytes = BytesIO()
    
    image = image.convert("RGB")
    image.save(img_bytes, format="JPEG")
    
    return img_bytes.getvalue()


async def open_pic(path: str) -> Image.Image:
    pic_path = Path(__file__).parent / "Data" / Path(path)
    
    return Image.open(pic_path)


async def open_icon(name: str, small: bool = False) -> Image.Image:
    icon_path = "student_icons/" + f"{name}.jpg"
    img = await open_pic(icon_path)

    if small:
        return img.resize((270, 290))
    else:
        return img.resize((404, 456))
        

async def save_icon(name: str, data: bytes) -> None:
    icon_path = ICONS_PATH / f"{name}.jpg"
    
    async with aiofiles.open(icon_path, "wb") as f:
        await f.write(data)
    

def create_msg(pic: Union[bytes, BytesIO], qq: str, texts: List[str]) -> MessageFactory:
    msg = MessageFactory([saa_image(pic), Text("\n"), Mention(qq)])
    
    for text in texts:
        msg += text
    
    return msg


def icon_is_empty() -> bool:
    return not any(os.listdir(ICONS_PATH))


def stored_icon_names() -> Set[str]:
    return set(
        [
            name.partition('.')[0]
            for name in os.listdir(ICONS_PATH)
        ]
    )


def rename_file(f):
    """
    采用新建文件, 覆盖原文件的方式, 杜绝数据损坏 
    """
    async def inner(data) -> None:
        rand_name, old_name = await f(data)
        os.remove(old_name)
        os.rename(rand_name, old_name)
        
    return inner  
    
    
async def load_cd() -> Union[Dict[str, int], Dict]:
    async with aiofiles.open(CD_PATH, "r") as f:
        return json.loads(
            await f.read()
        )
    

@rename_file
async def save_cd(cd: Dict[str, int]) -> Tuple[str, str]:
    async with aiofiles.open(rand_name := (CD_PATH.parent / f"{uuid.uuid4()}.json"), "w") as f:
        await f.write(json.dumps(cd))
    
    return str(rand_name), str(CD_PATH)
     
     
async def clear_cd() -> None:
    async with aiofiles.open(CD_PATH, "r") as f:
        await f.write(json.dumps({}))
    
    
async def load_white() -> Union[List[str], List]:
    async with aiofiles.open(WHITE_PATH, "r") as f:
        return json.loads(await f.read())
    

@rename_file
async def save_white(white_list: Union[List[str], List]) -> Tuple[str, str]:
    async with aiofiles.open(rand_name := (WHITE_PATH.parent / f"{uuid.uuid4()}.json"), "w") as f:
        await f.write(json.dumps(white_list))
        
        return str(rand_name), str(WHITE_PATH)