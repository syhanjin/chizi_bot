
from nonebot import on_command
import nonebot
from nonebot.adapters.cqhttp.event import MessageEvent, PrivateMessageEvent
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.permission import GROUP, PRIVATE
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from handles.message_builder import introduction, welcome_card

NAME = list(nonebot.get_driver().config.nickname)[0]
t1 = on_command(
    'test1', permission=PRIVATE, priority=1, block=False
)
t2 = on_command(
    'test2', priority=1, block=False
)


@t1.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    await bot.send(event, welcome_card(
        '欢迎',
        'https://sakuyark.com/static/images/icon.jpg',
        [('我就是测试',)],
        [('Sakuyark', 'https://sakuyark.com')]
    ))


@t2.handle()
async def _(bot: Bot, event: MessageEvent):
    await bot.send(
        event,
        f'我是{NAME}, 一个可爱的机器人，来自Sakuyark'
    )
