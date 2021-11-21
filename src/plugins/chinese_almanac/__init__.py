import datetime
import os
from string import capwords
import nonebot
import aiohttp

from bs4 import BeautifulSoup
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.plugin import on_command
from handles import HEADERS
from handles.image import FONT, Draw, ImgDraw
from handles.message_builder import image
from handles.text import *
from handles.zhongguose import *

root_path = os.path.join('.', 'res', 'chinese_almanac')
card_path = os.path.join(root_path, 'card')
if not os.path.exists(root_path):
    os.makedirs(root_path)
if not os.path.exists(card_path):
    os.makedirs(card_path)


async def chinese_almanac(date: 'datetime | None' = None) -> dict:
    """
    老黄历，来自 www.laohuangli.net 
    :param date: 日期，不传入则默认今天

    result:
    :attr ndate: 农历日期
    :attr gdate: 公历日期
    :attr ywarn: 今日所宜，警告
    :attr jwarn: 今日所忌，警告
    :attr jrsy:  今日所宜
    :attr jrsj:  今日所忌
    :attr jsyq:  吉神宜趋
    :attr xsyj:  凶煞宜忌
    :attr mqjq:  目前节气
    :attr xgjq:  下个节气
    :attr csw:   财神位 [x, f, c] 喜神，福神，财神
    :attr yygs:  阴阳贵神 [yang, yin] 阳贵神 阴贵神
    """
    result = {
        'ndate': '',
        'gdate': '',
        'ywarn': '',
        'jwarn': '',
        'jrsy':  '',
        'jrsj':  '',
        'jsyq':  '',
        'xsyj':  '',
        'mqjq':  '',
        'xgjq':  '',
        'csw': {'x': '', 'f': '', 'c': ''},
        'yygs': {'yang': '', 'yin': ''}
    }
    payload = date.__format__('%Y/%Y-%m-%d.html') if date is not None else ''
    async with aiohttp.ClientSession() as c:
        r = await c.get(
            'https://www.laohuangli.net/' + payload,
            headers=HEADERS
        )
        soup = BeautifulSoup((await r.text()), features='lxml')
    table = soup.select_one(
        '.cate-box.mt-10 .title-table-index.table-border-box table')
    bg_table = table.select_one('.middle-rowspan')
    result['ndate'] = space_multiple_to_one(
        bg_table.select_one('.p-relative').text)
    date2 = space_multiple_to_one(
        bg_table.select_one('.page-btn-box span').text)
    result['gdate'] = space_multiple_to_one(bg_table.select_one(
        '.middle-rowspan p:first-child').text)
    # 【日值岁破 大事勿用】
    tf3 = table.select('.table-three-div', limit=2)
    appropriates = []
    for i in tf3[0].select('.t-center span'):
        appropriates.append(delete_space(i.text))
    result['jrsy'] = appropriates
    w = tf3[0].select_one('.t-center')
    [i.decompose() for i in w('span')]
    result['ywarn'] = space_multiple_to_one(w.text)

    taboos = []
    for i in tf3[1].select('.t-center span'):
        taboos.append(delete_space(i.text))
    result['jrsj'] = taboos
    w = tf3[1].select_one('.t-center')
    [i.decompose() for i in w('span')]
    result['jwarn'] = space_multiple_to_one(w.text)

    tf5 = table.select('.table-five-div', limit=2)
    jsyq = ''
    for i in tf5[0].select('.t-center span'):
        jsyq += delete_space(i.text)
    result['jsyq'] = jsyq
    xsyj = ''
    for i in tf5[1].select('.t-center span'):
        xsyj += delete_space(i.text)
    result['xsyj'] = xsyj

    jq = table.select_one('.text-p').select('td')
    result['mqjq'] = jq[0].text
    result['xgjq'] = jq[1].text

    e = soup.select('.table-box2 .img-box .flex-1.t-center')
    for i in e:
        for j in i('strong'):
            j.decompose()
    csw = e[0].select('li')
    result['csw']['x'] = delete_space(csw[0].text)
    result['csw']['f'] = delete_space(csw[1].text)
    result['csw']['c'] = delete_space(csw[2].text)
    yygs = e[1].select('li')
    result['yygs']['yang'] = delete_space(yygs[0].text)
    result['yygs']['yin'] = delete_space(yygs[1].text)
    return result


async def make_almanac(date: 'datetime | None' = None) -> str:
    """
    构建黄历图片并返回路径
    """
    date = date or datetime.datetime.now()
    out_path = os.path.join(
        card_path,
        date.__format__('%Y-%m-%d')+'.jpg'
    )
    data = (await chinese_almanac(date))
    bg = Draw.make_bg(1200, 1500)
    draw = ImgDraw(bg)
    await draw.init()
    await draw.openfont(FONT)
    draw.pos = (0, 30)

    await draw.putTextCenter('今日黄历', 1200, 0, 30, fontsize=100, fill=MANJIANGHONG)
    await draw.putTextCenter(data['gdate'], 1200, 0, 10, fontsize=32)
    await draw.putTextCenter(data['ndate'], 1200, 0, 30, fontsize=32)
    tmp = draw.y
    await draw.putTextCenter('宜', 600, 0, 20, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(data['ywarn'], 600, 0, fontsize=32, fill=SHANCHAHONG)
    await draw.putTextCenter(linefeed(data['jrsy'], 15), 600, 0, 30, fontsize=32)
    maxy = draw.y
    draw.pos = (600, tmp)
    await draw.putTextCenter('忌', 600, 0, 20, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(data['jwarn'], 600, 0, fontsize=32, fill=SHANCHAHONG)
    await draw.putTextCenter(linefeed(data['jrsj'], 15), 600, 0, 30, fontsize=32)
    draw.pos = (0, max(maxy, draw.y))

    tmp = draw.y
    await draw.putTextCenter('吉神宜趋', 600, 0, 20, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(linefeed(data['jsyq'], 15), 600, 0, 30, fontsize=32)
    maxy = draw.y
    draw.pos = (600, tmp)
    await draw.putTextCenter('凶煞宜忌', 600, 0, 20, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(linefeed(data['xsyj'], 15), 600, 0, 50, fontsize=32)

    draw.pos = (0, max(maxy, draw.y))
    await draw.putTextCenter('节    气', 1200, 0, 40, fontsize=72, fill=YANHONG)
    draw.x = 50
    await draw.putTextCenter(data['mqjq'], 500, -1, fontsize=32)
    draw.x = 550
    await draw.putTextCenter('==>', 100, -1, fontsize=32)
    draw.x = 650
    await draw.putTextCenter(data['xgjq'], 500, 0, 50, fontsize=32)

    draw.x = 0
    await draw.putTextCenter('财神位', 1200, 0, 30, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(
        (
            '喜神', data['csw']['x'], '',
            '福神', data['csw']['f'], '',
            '财神', data['csw']['c']
        ), 1200, 0, 50, fontsize=50
    )
    draw.x = 0
    await draw.putTextCenter('阴阳贵神', 1200, 0, 30, fontsize=72, fill=YANHONG)
    await draw.putTextCenter(
        (
            '阳贵神', data['yygs']['yang'], '',
            '阴贵神', data['yygs']['yin']
        ), 1200, 0, 50, fontsize=50
    )

    draw.x = 800
    await draw.putText('临时版面 Sakuyark@2021', fill=(196, 196, 196))
    await draw.save(out_path)
    return os.path.abspath(out_path)


ca = on_command(
    '今日黄历', aliases={'黄历'},
    priority=2
)


@ca.handle()
async def _(bot: Bot, event: MessageEvent):
    path = (await make_almanac())
    await bot.send(event, image(path), at_sender=True)
