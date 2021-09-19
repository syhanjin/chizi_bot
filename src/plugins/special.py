
from typing import Optional
from nonebot.adapters.cqhttp.permission import GROUP
from nonebot.exception import IgnoredException
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.plugin import on_metaevent
from nonebot.typing import T_State


onEVENT = on_metaevent(priority=1, permission=GROUP, block=False)


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, state: T_State):

    if event.group_id == 457263503:
        matcher.stop_propagation()
