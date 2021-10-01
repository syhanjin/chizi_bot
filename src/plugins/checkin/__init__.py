from handles.image import ImgDraw
from nonebot.adapters.cqhttp.event import GroupMessageEvent
import pymongo
import datetime
from handles.group import User, make_query
import os
import json
import random

import nonebot
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
from PIL import Image, ImageDraw, ImageFont
# from utils.message_builder import image

checkin = on_command("签到", priority=5, permission=GROUP, block=True)

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
    def __init__(self, group_id: str, user_id: str):
        super().__init__(group_id, user_id)
        data = db.checkin.find_one(make_query(group_id, user_id))
        if data == None:
            data = {}

        def _(k, v): return data[k] if(k in data) else v
        self.last = _('last', None)
        self.continuity = _('continuity', 0)
        return None

    def checkin(self):
        # 信息变更
        self.now = datetime.datetime.now()
        if self.last:
            if (
                self.now
                - datetime.timedelta(
                    hours=self.now.hour,
                    minutes=self.now.minute,
                    seconds=self.now.second,
                    microseconds=self.now.microsecond
                )
            ) == (
                    self.last
                    - datetime.timedelta(
                        hours=self.last.hour,
                        minutes=self.last.minute,
                        seconds=self.last.second,
                        microseconds=self.last.microsecond
                    )
            ):
                return False
                pass
        # 今天凌晨
        zeroToday = self.now - datetime.timedelta(hours=self.now.hour, minutes=self.now.minute,
                                                  seconds=self.now.second, microseconds=self.now.microsecond)
        if self.last and self.last + datetime.timedelta(hours=24) >= zeroToday:
            self.continuity += 1
        else:
            self.continuity = 1
        self.last = self.now
        self.today_favor = round(rand(self.dfav[0], self.dfav[1]), 2)
        self.today_coin = int(rand(5, 20))
        self.add_favor(self.today_favor)
        self.coin += self.today_coin
        if self.admin == 5:
            self.label = '主仆'
        return True

    async def generate_card(self):
        # 生成图片
        # region 随机背景
        bg = os.path.join(root_path, 'H', str(random.randint(1, 30))+'.jpg')
        img = ImgDraw(bg)
        await img.init()
        img.resize((1920, 1080), Image.ANTIALIAS)
        font = os.path.join(
            '.', 'res', 'checkin', 'fonts', 'LXGWWenKai-Regular.ttf'
        )
        img.draw.rectangle((0, 400, 1920, 1080), fill=(216, 216, 216, 216))
        await img.openfont(font)

        # region 输出用户名 && QQ && sakuyark
        img.pos = 40, 10
        await img.putText(self.card, 0, fill=(255, 255, 255), fontsize=128, border=1.5)
        await img.putText(('QQ:', self.user_id), 0, fill=(255, 255, 255), fontsize=96, border=1.5)
        if self.user:
            await img.putText(('Sakuyark:', self.user), 0, fill=(255, 255, 255), fontsize=96, border=1.5)
        # endregion
        # region 输出连签
        img.pos = 40, 430
        await img.putText(u"Accumulative check-in for", 1, 15, fontsize=60)
        img.y = 410
        await img.putText(self.continuity, 1, 15, fill='#ff00ff', fontsize=80, border=1, borderFill=(200, 0, 200))
        img.y = 430
        await img.putText('days', 1, fontsize=60)
        # endregion
        # region 左侧 头像

        # endregion
        # region 中间 当前信息
        img.pos = 400, 600
        # 分割线
        img.draw.line((img.x, img.y, img.x, 950), fill='#000', width=3)
        # 内容
        img.x += 50
        img.y += 20
        await img.putText(('当前好感度 :', self.favor), 0, 15, fontsize=48)

        dx, h = 15, 40
        img.draw.rectangle(
            (img.x + dx, img.y, img.x + dx + 360, img.y + h), fill='#fff'
        )
        img.draw.ellipse(
            (img.x + dx + 340, img.y, img.x + dx+380, img.y + h), fill='#fff'
        )
        w = self.favor / self.fav_max * 340 + 40
        img.draw.rectangle(
            (img.x + dx, img.y, img.x + dx + w - 20, img.y + h), fill='#f0f'
        )
        img.draw.ellipse(
            (img.x + dx + w - 40, img.y, img.x + dx + w, img.y + h), fill='#f0f'
        )
        img.y += h+15
        await img.putText(
            ('· 与', NAME, '的关系 :', self.label), 0, fontsize=36
        )
        await img.putText(
            ('· ', NAME, '对你的态度 :', self.attitude), 0, fontsize=36
        )
        await img.putText(
            ('· 关系提升还需要:', round(self.fav_max - self.favor, 2), '好感度'), 0, 15, fontsize=36
        )
        await img.putText(
            ('时间: ', self.now.__format__('%Y-%m-%d %a %H:%M')), 0, fontsize=48
        )
        # endregion
        # region 右侧 今日签到信息 全部信息
        img.pos = 1150, 430
        await img.putText('今日签到', 0, 15, fontsize=72)
        img.x += 50
        await img.putText('好感度', -1, fontsize=60)
        img.x += 350
        await img.putText(('+', self.today_favor), 0, 15, fontsize=60, fill=(128, 64, 64))
        await img.putText(('+', str(self.today_coin)), -1, fontsize=60, fill=(128, 64, 64))
        img.x -= 350
        await img.putText('金币', 0, 60, fontsize=60)
        await img.putText(('金币总数:', self.coin), fontsize=60)
        # endregion
        # region 输出水印
        img.pos = 1750, 20
        await img.putText(
            self.now.__format__('%m/%d'), fill=(255, 255, 255), fontsize=48, border=1
        )
        img.pos = 1600, 1020
        await img.putText('Sakuyark@2021', fill=(128, 128, 128), fontsize=36)
        # endregion
        out_path = os.path.join(root_path, 'cards', self.now.__format__(
            '%Y%m%d%H%M%S')+str(random.randint(10, 99))+'.jpg')
        await img.save(out_path)
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
            }, True
        )

# -- ------ --


def rand(st, ed): return random.random()*(ed-st) + st


@checkin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = json.loads(event.json())
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    c = Checkin(group_id, user_id)
    c.update_from_event(event)
    if not c.checkin():
        await bot.send(event, '你今天已经签过到了，明天再来吧~~', at_sender=True)
        return
    src = await c.generate_card()
    await c.save()
    await bot.send(event, ms.image('file://'+src), at_sender=True)
