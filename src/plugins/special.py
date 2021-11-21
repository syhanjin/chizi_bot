
from nonebot.exception import IgnoredException
from nonebot.adapters.cqhttp.permission import GROUP
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.plugin import on_message, on_metaevent
from nonebot.typing import T_State


onEVENT = on_message(priority=1, permission=GROUP, block=False)


# @run_preprocessor
# async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, state: T_State):
#     if not isinstance(event, GroupMessageEvent):
        
#         pass
#     elif event.group_id == 457263503:
#         raise IgnoredException("此群已屏蔽")
