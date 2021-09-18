
from typing import Optional
from nonebot.exception import IgnoredException
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
from nonebot.typing import T_State

@run_postprocessor
async def do_something(matcher: Matcher, exception: Optional[Exception], bot: Bot, event: GroupMessageEvent, state: T_State):
    

    if event.group_id == 457263503:
        raise IgnoredException('此群不做处理')