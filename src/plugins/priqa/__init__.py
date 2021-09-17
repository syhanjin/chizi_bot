import datetime
import re
import pandas as pd

from nonebot.adapters.cqhttp.event import PrivateMessageEvent
import json
from nonebot import on_message
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import PRIVATE
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

priqa = on_message(permission=PRIVATE, priority=99, block=True)
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~“”？，！【】（）、。：；’‘……￥·"""


@priqa.handle()
def _priqa(bot: Bot, event: PrivateMessageEvent):
    text = event.raw_message
    # 去除消息中所有空格、回车以及标点
    text = text.replace(' ', '').replace('\n', '').translate(
        str.maketrans('', '', punctuation))
