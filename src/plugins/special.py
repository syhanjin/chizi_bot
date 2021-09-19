
from typing import Optional
from nonebot.exception import IgnoredException
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.typing import T_State


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, state: T_State):

    if event.group_id == 457263503:
        await matcher.finish()
        matcher.stop_propagation()
