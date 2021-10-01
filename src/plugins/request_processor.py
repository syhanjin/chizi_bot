
from nonebot.adapters.cqhttp.event import FriendRequestEvent
from nonebot.permission import REQUEST
from handles import group
import json
from nonebot import on_request
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP

friend_request = on_request(priority=1, block=False)


@friend_request.handle()
def _(bot: Bot, event: FriendRequestEvent):
    bot.call_api('set_friend_add_request', flag=event.flag, approve=True)
