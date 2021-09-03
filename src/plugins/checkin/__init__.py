import datetime
import os
import random

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot, MessageEvent
from nonebot.typing import T_State
from PIL import Image, ImageDraw, ImageFont
from utils.message_builder import image

checkin = on_command("签到", priority=5)

# -- 数据库 --
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']
# -- ------ --

NAME = list(nonebot.config.nickname)[0]
root_path = os.path.join('.', 'res', 'sign')
card_ratio = 16 / 9

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
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await checkin.send(event.get_session_id())
    # data = db.user.find_one({'group_id': event.grou})
