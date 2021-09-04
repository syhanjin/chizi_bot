
import datetime
import re

from nonebot.adapters.cqhttp.event import GroupMessageEvent
from handles import User
import json
from nonebot import on_message
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
import pymongo


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


# 判定刷屏
async def flood(bot: Bot, event: GroupMessageEvent, this: Msg, user: User):
    f4 = await this.fisrt_seconds(4)
    if f4.count() >= 4 and user.admin == 0:
        # 4秒内发送消息4次则禁言 60s
        await bot.call_api(
            'set_group_ban',
            user_id=this.user_id,
            group_id=this.group_id,
            duration=60
        )
        # 执行消息撤回
        for i in list(f4):
            await bot.call_api('delete_msg', message_id=i['id'])
        await bot.call_api('delete_msg', message_id=this.id)


# 对群名片识别
async def cards(bot: Bot, event: GroupMessageEvent, this: Msg, user: User):
    group_id = event.group_id
    data = db.cards.find_one({'group_id': group_id})
    if not int(user.user_id) in data['special'] and not re.search(data['reg'], user.card, re.I):
        await bot.send(event,ms.text('请修改名片，名片格式 ' + data['format']),at_sender=True)
    

# async def keyword_delete(bot: Bot, event: MessageEvent, user: User):
#     if not isinstance(event, GroupMessageEvent) or user.admin > 0:
#         return
    