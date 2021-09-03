
import datetime
from handles import User
import json
from nonebot import on_message
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
import pymongo


client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

main = on_message(permission=GROUP, block=False)


class Msg:
    def __init__(self, group_id, user_id, msg):
        self.group_id = group_id
        self.user_id = user_id
        # self.text = msg.get('raw_message')
        self.id = msg.get('message_id')
        self.time = datetime.datetime.fromtimestamp(msg['time'])
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
async def _(bot: Bot, event: MessageEvent):
    msg = json.loads(event.json())
    group_id, user_id = msg['group_id'], msg['user_id']
    this = Msg(group_id, user_id, msg)
    await this.save()
    user = User(str(group_id), str(user_id))
    # 扩展处理
    await flood(bot, event, this, user)


async def flood(bot: Bot, event: MessageEvent, this: Msg, user: User):
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
