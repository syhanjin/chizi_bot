
import datetime
import re
import numpy as np
import pandas as pd

from nonebot.adapters.cqhttp.event import GroupMessageEvent
from handles import User
import json
from nonebot import on_message
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
import pymongo

punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~“”？，！【】（）、。：；’‘……￥·"""

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

main = on_message(permission=GROUP, block=False)


class Msg:
    def __init__(self, group_id, user_id, event: GroupMessageEvent):
        self.group_id = group_id
        self.user_id = user_id
        self.id = event.message_id
        self.time = datetime.datetime.fromtimestamp(event.time)
        pass

    async def fisrt_seconds(self, seconds):
        return db.msg.find({
            'group_id': self.group_id,
            'user_id': self.user_id,
            'time': {'$gte': self.time - datetime.timedelta(seconds=seconds)}
        })

    async def save(self):
        db.msg.insert_one({
            'group_id': self.group_id,
            'user_id': self.user_id,
            'time': self.time,
            'id': self.id
        })


@main.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id, user_id = event.group_id, event.user_id
    this = Msg(group_id, user_id, event)
    await this.save()
    user = User(str(group_id), str(user_id))
    user.update_from_event(event)
    # 扩展处理
    await flood(bot, event, this, user)
    await cards(bot, event, this, user)
    await keyword_delete(bot, event, this, user)


# 判定刷屏
async def flood(bot: Bot, event: GroupMessageEvent, this: Msg, user: User):
    f10 = await this.fisrt_seconds(10)
    if f10.count() >= 10 and user.admin == 0:
        # 10秒内发送消息10次则禁言 300s
        await bot.call_api(
            'set_group_ban',
            user_id=this.user_id,
            group_id=this.group_id,
            duration=300
        )
        # 执行消息撤回
        for i in list(f10):
            await bot.call_api('delete_msg', message_id=i['id'])
        await bot.call_api('delete_msg', message_id=this.id)


# 对群名片识别
async def cards(bot: Bot, event: GroupMessageEvent, this: Msg, user: User):
    group_id = event.group_id
    data = db.cards.find_one({
        'group_id': group_id,
        'special': {'$nin': [int(user.user_id)]}
    })
    if data is None:
        return
    if not re.search(data['reg'], user.card, re.I):
        await bot.send(event, ms.text('请修改名片，名片格式 ' + data['format']), at_sender=True)


# 关键字拦截
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~“”？，！【】（）、。：；’‘……￥·"""
# 载入缓存
kws = pd.DataFrame(list(db.kw.find()))
kws = kws[kws['opened']].groupby(['group_id', 'degree'])


def _kw_op(group_id, text, degree):
    # 获取分组 群号
    gp = kws.get_group((group_id, degree))
    # 识别此关键字
    return gp[[i in text for i in gp['kw'].values]]


def kw_op(group_id, text):
    ops = pd.DataFrame([])
    if (group_id, 1) in kws.groups:
        ops = ops.append(_kw_op(group_id, text, 1))
    if (group_id, 2) in kws.groups:
        text = text.replace(' ', '')
        ops = ops.append(_kw_op(group_id, text, 2))
    if (group_id, 3) in kws.groups:
        text = text.translate(str.maketrans('', '', punctuation))
        ops = ops.append(_kw_op(group_id, text, 3))
    # 判断是否有条目符合
    if ops.shape[0] == 0:
        return None
    # 识别主操作，如果不包含kick即为ban
    main_op = 'kick' if ('kick' in ops['main_op'].unique()) else 'ban'
    # 副操作 -- 使用set去重
    seco_op = set(ops['seco_op'].sum())
    # 识别数据
    if main_op == 'ban':
        ban_time = ops['ban_time'].max()
    else:
        kick_warn = ops['kick_warn'].min()
        # 暂不开启踢出识别
        return None
    return (main_op, seco_op, (ban_time))


async def keyword_delete(bot: Bot, event: GroupMessageEvent, this: Msg, user: User):
    if user.admin > 0:
        return
    text = event.raw_message
    op = kw_op(event.group_id, text)
    if op is None:
        return
    if op[0] == 'ban':
#         await bot.send(event, f'''【关键字拦截】不进行操作执行--此消息触犯说明：
# 主操作：禁言
# 副操作：{op[1]}
# 时间：{op[2]}
# ''')
        await bot.call_api('set_group_ban', group_id=event.group_id,
                     user_id=event.user_id, duration=op[2])

        # 报告管理暂关
        # if 'report' in op[1]:
        # 如果需要报告管理员
        # await bot.call_api('')
