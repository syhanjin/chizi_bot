
from nonebot import on_command
from nonebot.adapters.cqhttp.event import MessageEvent, PrivateMessageEvent
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.permission import GROUP, PRIVATE
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from handles.message_builder import welcome_card

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
    await bot.send(event, ms.xml(
        {
            'data': """<?xml version='1.0' encoding='UTF-8' ?><msg serviceID="104" templateID="1" brief="大家好，我是丙实。金牛座男一枚~"><item layout="2"><picture cover="" /><title>新人入群</title></item><source /></msg>""",
            'resid': 104
        }
    ))
