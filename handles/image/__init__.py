import os
from typing import Union
from PIL import Image, ImageDraw, ImageFont


class ImgDraw(object):
    """
    打开图片并生成一张与图片等大的画布
    请在对象创建完成后调用
    await obj.init()
    绘制时请调用 obj.draw
    """
    def __init__(self, path: str) -> None:
        self.path = path
        self.x = 0
        self.y = 0
        self.__font = None

    async def init(self) -> None:
        if not os.path.exists(self.path):
            raise OSError('Flie is not exists')
        self.img = Image.open(self.path)
        self.__newDraw()

    def __newDraw(self) -> None:
        self.__draw = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.__draw)

    async def __putBorder(self, pos: 'tuple[int, int]', text: str, fill: 'tuple[int, int, int]') -> None:
        self.draw.text(pos, text, font=self.font, fill=fill)

    async def openfont(self, path: str, fontsize: int = 16) -> None:
        if not os.path.exists(path):
            raise OSError('File is not exists')
        self.__font = ImageFont.truetype(path, size=fontsize)

    async def putText(
        self,
        text: 'str | tuple',
        direction: int = 1,
        interval: int = 0,
        font: 'str' = None,
        fontsize: int = 16,
        fill: 'tuple[int, int, int] | str' = (0, 0, 0),
        border: int = 0,
        borderFill: 'tuple[int, int, int] | str' = (0, 0, 0)
    ) -> None:
        """
        说明：
            在图像的画布上打印一行文字
        参数：
            :param text: 文字，若传入元组则类似print打印方案
            :param direction: 坐标移动方向 -1:不移动，0:向下，1:向右
            :param interval: 间隔，往direction方向的偏移量
            :param font: 字体文件路径, 默认采用上次字体
            :param fontsize: 字体大小
            :param fill: 字体填充颜色
            :param border: 边框大小
            :param borderFill: 边框填充颜色
        """
        if font is not None:
            await self.openfont(font, fontsize)
        else:
            self.__font.size=fontsize
        if type(text) == type(()):
            tmp, text = text, ''
            for i in tmp:
                text += str(i) + ' '
        text = str(text)
        if border > 0:
            # 文字阴影
            # thin border
            self.__putBorder((self.x-border, self.y), text, borderFill)
            self.__putBorder((self.x+border, self.y), text, borderFill)
            self.__putBorder((self.x, self.y-border), text, borderFill)
            self.__putBorder((self.x, self.y+border), text, borderFill)
            # thicker border
            self.__putBorder((self.x-border, self.y-border), text, borderFill)
            self.__putBorder((self.x+border, self.y-border), text, borderFill)
            self.__putBorder((self.x-border, self.y+border), text, borderFill)
            self.__putBorder((self.x+border, self.y+border), text, borderFill)
        self.draw.text((self.x, self.y), text, font=self.font, fill=fill)
        deviation = self.draw.textsize(text, font=self.font, spacing=0)
        if direction == 0:
            self.y += deviation[1] + 2*border + interval
        elif direction == 1:
            self.x += deviation[0] + 2*border+ interval

    def resize(
        self,
        size: 'tuple[int, int]',
        resample: '_Resample | None' = ...,
        box: 'tuple[float, float, float, float] | None' = ...,
        reducing_gap: 'float | None' = ...,
    ) -> None:
        """
        说明：
            重置对象大小，参数与 PIL.Image.resize 一样
        注意：
            重置后会清空画布！！！
        """
        self.img = self.img.resize(size, resample, box, reducing_gap)
        self.__newDraw()

    def composite(self) -> None:
        """
        将画布盖到原图上并清空画布
        """
        img = Image.alpha_composite(self.img.convert('RGBA'), self.__draw)
        self.img = img.convert("RGB")
        self.__newDraw()

    async def save(self, path: str) -> None:
        self.composite()
        self.img.save(path)

    @property
    def pos(self) -> 'tuple[int, int]':
        return (self.x, self.y)

    @pos.setter
    def pos(self, pos: 'tuple[int, int]') -> None:
        self.x = pos[0]
        self.y = pos[1]

    @property
    def font(self) -> ImageFont.FreeTypeFont:
        if self.__font is None:
            raise NameError('has not opened a font')
        return self.__font
