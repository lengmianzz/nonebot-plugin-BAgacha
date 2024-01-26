from PIL import Image
from typing import Sequence, Tuple, List
from functools import reduce

from .utils import open_pic, open_icon


EVERY_ROW = 5
WHITE_COLOR = (255, 255, 255)
SEMITRANSPARENT_WHITE_COLOR = (255, 255, 255, 125)


class Draw:
    @staticmethod
    def _scaled_with_aspect_ratio(image: Image.Image, embed_image_size: Tuple[int, int]) -> Image.Image:
        scale_factor = max((embed_image_size[1] * 5) / image.width, 1)
        
        return image.resize((int(scale_factor * image.width), int(scale_factor * image.height)))
    
    
    @staticmethod
    def _calculate_interval(bg_size: Tuple[int, int], icon_size: Tuple[int,int], numbers: int) -> Tuple[int, int]:
        every_col, m = divmod(numbers, EVERY_ROW)
        
        if m: 
            every_col += 1

        x_i = (bg_size[0] - (icon_size[0] * EVERY_ROW)) // (EVERY_ROW + 1)
        y_i = (bg_size[1] - (icon_size[1] * every_col)) // (every_col + 1)
        
        return x_i, y_i
    
    
    @staticmethod
    def _add_white_mask(image: Image.Image) -> Image.Image:
        image.paste(i := Image.new("RGBA", (image.width, image.height), SEMITRANSPARENT_WHITE_COLOR), mask=i)
        
        return image
    
    
    @staticmethod
    def _speciff_location_paste(embed_image_size: Tuple[int, int], x_i: int, y_i: int):
        row = 0
        
        x = x_i
        y = y_i
        
        x_interval = x_i + embed_image_size[0]
        y_interval = y_i + embed_image_size[1]
        
        def inner(pasted_pic: Image.Image, pic: Image.Image) -> Image.Image:
            nonlocal x, y, row

            pasted_pic.paste(pic, (x, y))

            row += 1
            x += x_interval

            if row % 5 == 0:
                x = x_i
                y += y_interval
                
            return pasted_pic
        
        return inner
    
    
    @classmethod
    async def embed_into_background(cls, names: List[str], small: bool) -> Image.Image:
        icons = [await open_icon(name, small=small) for name in names]
        icon_size = icons[0].size
        
        bg = cls._scaled_with_aspect_ratio(
            cls._add_white_mask(await open_pic("background.jpg")),
            icon_size
        )
        
        interval = cls._calculate_interval(bg.size, icon_size, len(icons))
        paste_func = cls._speciff_location_paste(icon_size, *interval)
        
        return reduce(paste_func, [bg] + icons)


async def embed_ups(names: Sequence[str]) -> Image.Image:
    images = [await open_icon(name) for name in names]
    height, width = images[0].size
    
    res = Image.new("RGB", (len(images) * height, width), WHITE_COLOR)

    for i, icon in enumerate(images):
        res.paste(icon, (height * i, 0))
        
    return res