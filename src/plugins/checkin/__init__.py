import datetime
from handles import User
import os
import random

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from PIL import Image, ImageDraw, ImageFont
# from utils.message_builder import image

checkin = on_command("签到", priority=5)

# -- 数据库 --
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']
# -- ------ --

NAME = list(nonebot.get_driver().config.nickname)[0]
root_path = os.path.join('.', 'res', 'sign')
card_ratio = 16 / 9


# -- 签到类 --
class Checkin(User):
    def __init__(self, group_id, user_id):
        super().__init__(group_id, user_id)
        data = db.checkin.find_one({'group_id':group_id, 'user_id': user_id})
        self.create(data)
    
    def create(self, data):
        if data == None:
            data = {}
        def _(k, v): return data[k] if(k in data) else v
        self.last = _('last', None)
        self.coin = _('coin', 0)

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


async def create_data(msg):
    data = {'qq': msg['user_id'], 'group': msg['group_id']}
    data['favorLevel'] = 0      # 好感等级
    data['continuity'] = 0      # 连续签到
    data['last'] = None         # 上次签到时间
    return data

@checkin.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # if event.get_event_name() != 'message.group.normal':
    #     return
    # group_id = event.get_session_id().split('_')[1]
    # user_id = event.get_user_id()
    # user = User(group_id, user_id)
    checkin.send(event.get_message())


