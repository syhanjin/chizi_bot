
import re
import pymongo
from utils.private import User

from nonebot import on_command
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.permission import PRIVATE

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']

c_number = re.compile('^([CK]\d{4})(\d{2})$')
identity = on_command(
    "identity", aliases={'身份验证', '验证'}, priority=3, block=True, permission=PRIVATE
)


@identity.handle()
async def _identity(bot: Bot, event: PrivateMessageEvent, state: T_State):
    state['count'] = 0
    await bot.send(event, '身份验证，目前仅支持[雅礼洋湖实验中学(YY)]的身份认证')


@identity.got('number', prompt='请输入学号 C/K+四位班级+学号 (例：K211101)')
async def _identity_class(bot: Bot, event: PrivateMessageEvent, state: T_State):
    m = c_number.match(state['number'].upper())
    if m is None:
        await identity.reject("学号输入不正确，请重新输入")
    state['class'] = m.group(1)
    state['number'] = m.group(2)


@identity.got('name', prompt='请输入姓名')
async def _identity_name(bot: Bot, event: PrivateMessageEvent, state: T_State):
    name = state['name']
    class_ = state['class']
    number = state['number']
    if (name or class_ or number) is None:
        await identity.finish('数据异常')

    user = User(event.user_id)
    user.update_from_event(event)
    if (await user.set_class('YY', class_, number, name)):
        await user.save()
        await identity.finish(f'设定完毕，{class_}{number}: {name}')
    else:
        state['count'] += 1
        if state['count'] >= 3:
            await identity.finish(f'验证失败，请重新验证')
        else:
            await identity.reject(f'学校 YY, 班级 {class_}, 姓名验证失败，请重发')
