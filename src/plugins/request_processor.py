
import nonebot
from nonebot.adapters.cqhttp.event import FriendRequestEvent, GroupRequestEvent
from nonebot.permission import REQUEST
from handles import group
import json
from nonebot import on_request
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP

from handles.message_builder import introduction

NAME = list(nonebot.get_driver().config.nickname)[0]
friend_request = on_request(priority=1, block=True)
group_request = on_request(priority=1,block=True)


@friend_request.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    await bot.call_api('set_friend_add_request', flag=event.flag, approve=True)

@group_request.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == 'invite':
        if event.user_id == 2819469337:
            await bot.call_api(
                'set_group_add_request',
                sub_type=event.sub_type,
                flag=event.flag
            )
            await bot.send(
                event,
                introduction(f'我是{NAME}, 一个可爱的机器人，来自Sakuyark')
            )
        else:
            await bot.call_api(
                'set_group_add_request',
                sub_type=event.sub_type,
                flag=event.flag,
                approve=False,
                reason="您没有足够的权限"
            )
    
