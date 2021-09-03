import pymongo
import datetime
from handles import User, make_query
import os
import json
import random

import nonebot
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.adapters.cqhttp.permission import GROUP
from PIL import Image, ImageDraw, ImageFont
# from utils.message_builder import image

checkin = on_command("签到", priority=5, permission=GROUP)

# -- 数据库 --

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']
# -- ------ --

NAME = list(nonebot.get_driver().config.nickname)[0]
root_path = os.path.join('.', 'res', 'checkin')
card_ratio = 16 / 9


# -- 签到类 --
class Checkin(User):
    async def __init__(self, group_id: str, user_id: str):
        await super().__init__(group_id, user_id)
        data = db.checkin.find_one(make_query(group_id, user_id))
        await self.create(data)
        return None

    async def create(self, data):
        if data == None:
            data = {}
        async def _(k, v): return data[k] if(k in data) else v
        self.last = await _('last', None)
        self.continuity = await _('continuity', 0)

    async def checkin(self):
        # 信息变更
        self.now = datetime.datetime.now()
        # 今天凌晨
        zeroToday = self.now - datetime.timedelta(hours=self.now.hour, minutes=self.now.minute,
                                                  seconds=self.now.second, microseconds=self.now.microsecond)

        if self.last and self.last + datetime.timedelta(hours=24) >= zeroToday:
            self.continuity += 1
        else:
            self.continuity = 1
        self.last = self.now
        self.today_favor = round(await rand(self.dfav[0], self.dfav[1]), 2)
        self.today_coin = int(await rand(5, 20))
        await self.add_favor(self.today_favor)
        self.coin += self.today_coin
        if self.admin == 5:
            self.label = '主仆'

    async def generate_card(self):
        # 生成图片
        # region 随机背景
        bg = os.path.join(root_path, 'H', str(random.randint(1, 30))+'.jpg')
        img = Image.open(bg)
        img = img.resize((1920, 1080), Image.ANTIALIAS)
        tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
        # endregion
        # region 构造画布
        draw = ImageDraw.Draw(tmp)
        fontpath = os.path.join('.', 'res', 'checkin', 'fonts',
                                'LXGWWenKai-Regular.ttf')
        draw.rectangle((0, 400, 1920, 1080), fill=(216, 216, 216, 216))
        # endregion

        # region 输出用户名 && QQ && sakuyark
        y = 10
        y += putText(draw, 40, y, self.card, font=fontpath,
                     fill=(255, 255, 255), fontsize=128, border=1.5)[1]
        y += putText(draw, 40, y, ('QQ:', self.user_id), font=fontpath,
                     fill=(255, 255, 255), fontsize=96, border=1.5)[1]
        if self.user:
            putText(draw, 40, y, ('Sakuyark:', self.user), font=fontpath, fill=(
                255, 255, 255), fontsize=96, border=1.5)
        # endregion
        # region 输出连签
        x = 40
        x += putText(draw, x, 430, u"Accumulative check-in for",
                     font=fontpath, fontsize=60)[0]
        x += 15
        x += putText(
            draw, x, 410, self.continuity,
            font=fontpath, fill='#ff00ff', fontsize=80,
            border=1, borderFill=(200, 0, 200)
        )[0]
        x += 15
        putText(draw, x, 430, 'days',
                font=fontpath, fontsize=60)
        # endregion
        # region 输出上次签到时间
        '''
        x = 1180
        x += putText(draw, x, 430, u"上次签到", font=fontpath, fontsize=60)[0]
        x += 30
        putText(draw, x, 430, last.__format__('%Y-%m-%d') if(last)
                else '无', font=fontpath, fontsize=60, fill=(216, 64, 64))
        '''
        # endregion

        # region 左侧 头像

        # endregion

        # region 中间 当前信息
        x, y = 400, 600
        # 分割线
        draw.line((x, y, x, 950), fill='#000', width=3)
        # 内容
        x += 50
        y += 20
        y += putText(draw, x, y, ('当前好感度 :',
                                  self.favor), font=fontpath, fontsize=48)[1]
        y += 15
        dx, h = 15, 40
        draw.rectangle((x + dx, y, x + dx + 360, y + h), fill='#fff')
        draw.ellipse((x + dx + 340, y, x + dx+380, y + h), fill='#fff')
        w = self.favor / self.fav_max * 340 + 40
        draw.rectangle((x + dx, y, x + dx + w - 20, y + h), fill='#f0f')
        draw.ellipse((x + dx + w - 40, y, x + dx + w, y + h), fill='#f0f')
        y += h+15
        y += putText(
            draw, x, y,
            ('· 与', NAME, '的关系 :', self.label),
            font=fontpath, fontsize=36
        )[1]
        y += putText(
            draw, x, y,
            ('· ', NAME, '对你的态度 :', self.attitude),
            font=fontpath, fontsize=36
        )[1]
        y += putText(
            draw, x, y,
            ('· 关系提升还需要:', self.fav_max - self.favor, '好感度'),
            font=fontpath, fontsize=36
        )[1]
        y += 15
        y += putText(
            draw, x, y,
            ('时间: ', self.now.__format__('%Y-%m-%d %a %H:%M')),
            font=fontpath, fontsize=48
        )[1]
        # endregion

        # region 右侧 今日签到信息 全部信息
        x, y = 1150, 430
        y += putText(draw, x, y, '今日签到', font=fontpath, fontsize=72)[1]
        x += 50
        y += 15
        txy = putText(draw, x, y, '好感度', font=fontpath, fontsize=60)
        putText(draw, x + 350, y, ('+', self.today_favor),
                font=fontpath, fontsize=60, fill=(128, 64, 64))
        y += txy[1]
        y += 15
        txy = putText(draw, x, y, '金币', font=fontpath, fontsize=60)
        putText(draw, x + 350, y, ('+', str(self.coin)),
                font=fontpath, fontsize=60, fill=(128, 64, 64))
        y += txy[1] + 60
        y += putText(draw, x, y,
                     ('金币总数:', self.today_favor), font=fontpath, fontsize=60)[1]
        # endregion

        # region 输出水印
        putText(draw, 1750, 20, self.now.__format__('%m/%d'),
                font=fontpath, fill=(255, 255, 255), fontsize=48,
                border=1
                )
        putText(draw, 1600, 1020, 'Sakuyark@2021',
                font=fontpath, fill=(128, 128, 128), fontsize=36)
        # endregion

        # region 合成并保存
        img = Image.alpha_composite(img.convert('RGBA'), tmp)
        img = img.convert("RGB")
        out_path = os.path.join(root_path, 'cards', self.now.__format__(
            '%Y%m%d%H%M%S')+str(random.randint(10, 99))+'.jpg')
        img.save(out_path)
        # endregion
        return os.path.abspath(out_path)

    async def save(self):
        await super().save()
        db.checkin.update_one(
            make_query(self.group_id, self.user_id),
            {
                '$setOnInsert': make_query(self.group_id, self.user_id),
                '$set': {
                    'last': self.last,
                    'continuity': self.continuity,
                }
            },
            {'upsert': True}
        )

# -- ------ --


async def rand(st, ed): return random.random()*(ed-st) + st


async def putText(draw, x, y, text: 'str | tuple', font='微软雅黑', fontsize=16, fill=(0, 0, 0), border=0, borderFill=(0, 0, 0)):
    font = ImageFont.truetype(font, size=fontsize)
    if type(text) == type(()):
        tmp = text
        text = ''
        for i in tmp:
            text += str(i) + ' '
    text = str(text)
    if border > 0:
        # 文字阴影
        # thin border
        draw.text((x-border, y), text, font=font, fill=borderFill)
        draw.text((x+border, y), text, font=font, fill=borderFill)
        draw.text((x, y-border), text, font=font, fill=borderFill)
        draw.text((x, y+border), text, font=font, fill=borderFill)
        # thicker border
        draw.text((x-border, y-border), text, font=font, fill=borderFill)
        draw.text((x+border, y-border), text, font=font, fill=borderFill)
        draw.text((x-border, y+border), text, font=font, fill=borderFill)
        draw.text((x+border, y+border), text, font=font, fill=borderFill)
    draw.text((x, y), text, font=font, fill=fill)
    return draw.textsize(text, font=font, spacing=0)


@checkin.handle()
async def _(bot: Bot, event: MessageEvent):
    msg = json.loads(event.json())
    group_id = str(msg['group_id'])
    user_id = str(msg['user_id'])
    c = await Checkin(group_id, user_id)
    c.update_from_msg(msg)
    await c.checkin()
    src = await c.generate_card()
    checkin.send(MessageSegment.image(src))

