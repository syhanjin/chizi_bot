import asyncio
from os import stat
import random
import re
import aiohttp
import datetime
from bs4 import BeautifulSoup

import nonebot
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent, PrivateMessageEvent
from nonebot.plugin import on_command, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State

from handles.message_builder import face, text


ft = on_regex(
    '.*(算.{0,2}[命卦]|卜.{0,2}卦).*', rule=to_me()
)


def is_all_zh(s):
    for c in s:
        if not ('\u4e00' <= c <= '\u9fa5'):
            return False
    return True


def processing_text(text: str, deletions: list = [], delete_space: bool = False, line_feed: bool = False):
    text = text.replace(u'\xa0', u' ').replace(u'\u3000', '  ')
    if line_feed:
        text = text.replace('\r\n', u'\n').replace(
            '\n', u'\n').replace('\r', u'\n')
    else:
        text = text.replace('\r', '').replace('\n', '')
    if delete_space:
        text = text.replace(' ', '').strip()
    else:
        text = text.strip()
    for i in deletions:
        text = text.replace(i, '')
    return text


async def fortuneTelling(
        ln: str,
        fn: str,
        sex: int,
        date: datetime,
        bt: str = ''
):
    """
    说明：
        八字算命(来源 http://www.dajiazhao.com/sm )
        字典数据说明：
        - info str		基本信息
        - name str		姓名
        - birthday
            - gc str    公历生日
            - lc str    农历生日
        - wxsx str      五行属相
        - bz list       八字
        - wx list       五行
        - ny list       纳音
        - bzwxgs list   八字五行个数, [金, 木, 水, 火, 土]
        - sjys str      四季用神参考
        - qtbjdhys str  穷通宝鉴调候用神参考
        - rgxx str      日干心性
        - rgzcs str     日干支层次
        - rgzfx str     日干支分析
        - wxskzhyj str  五行生克制化宜忌
        - wxzx str      五行之性
        - szwxskxb str  四柱五行生克中对应需补的脏腑和部位
        - syfw str      宜从事行业与方位
        - sxgx str      生肖个性
        - smth str      三命通会
        - yrsml         月日时命理
            - y list    月 |
            - r list    日 | => [标题, 文本]
            - s list    时 |

    参数：
        :param ln: Lastname 姓，汉字
        :param fn: Firstname 名，汉字
        :param sex: 性别，[int]: 1.男, 2.女
        :param date: 出生日期，精确到分钟
        :param bt: 血型，[A, B, O, AB, ]
    """
    if not is_all_zh(ln):
        raise ValueError('ln must be a string.')
    if len(ln) > 2 or len(ln) <= 0:
        raise ValueError('1 <= len(ln) <= 2')
    if not is_all_zh(fn):
        raise ValueError('fn must be a string.')
    if isinstance(sex, int):
        if sex not in [1, 2]:
            raise ValueError('sex must be 1 or 2')
    else:
        raise TypeError('sex must be a int')

    async with aiohttp.ClientSession() as c:
        r = await c.post(
            'http://www.dajiazhao.com/sm/scbz.asp',
            data=f'''xing={ln}&ming={fn
			}&xingbie={('男' if (sex == 1) else '女')
			}&xuexing={bt
			}&nian={date.year}&yue={date.month}&ri={date.day
			}&hh={date.hour}&mm={date.minute}'''.encode('gb2312'),
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
    soup = BeautifulSoup((await r.text('gb2312')), features="lxml")
    if len(soup.select('.ttop2 dl dd font')) == 0:
        # 判定无结果
        raise RuntimeError('Unable to get data.')
    # 开始分析处理
    result = {
        'info': '',		# 基本信息
        'name': '',		# 姓名
        'birthday':
        {
            'gc': '',   # 公历生日
            'lc': ''    # 农历生日
        },
        'wxsx': '',		# 五行属相
        'bz': [],		# 八字
        'wx': [],		# 五行
        'ny': [],       # 纳音
        'bzwxgs': [],   # 八字五行个数, [金, 木, 水, 火, 土]
        'sjys': '',     # 四季用神参考
        'qtbjdhys': '',  # 穷通宝鉴调候用神参考
        'rgxx': '',     # 日干心性
        'rgzcs': '',    # 日干支层次
        'rgzfx': '',    # 日干支分析
        'wxskzhyj': '',  # 五行生克制化宜忌
        'wxzx': '',     # 五行之性
        'szwxskxb': '',  # 四柱五行生克中对应需补的脏腑和部位
        'syfw': '',     # 宜从事行业与方位
        'sxgx': '',     # 生肖个性
        'smth': '',     # 三命通会
        'yrsml': {      # 月日时命理
            'y': [],    # 月    \
            'r': [],    # 日    | => [标题, 文本]
            's': []     # 时    /
        },
    }
    # region main
    # 获得当前算命者信息
    ttopp2 = soup.select_one('.ttop2 dl dd')
    result['info'] = processing_text(ttopp2.text)
    # 分析表格
    tables = soup.select('table tbody')
    # table1
    t1 = tables[0]
    trs = t1.select('tr')
    tr1 = trs[0]
    # 名字
    result['name'] = processing_text(
        tr1.select('td')[0].text, delete_space=True
    )
    # 公历生日
    gc = tr1.select('td:nth-child(n+4):not(:last-child)')
    for i in gc:
        result['birthday']['gc'] += i.text
    # 五行属相
    tfes = tr1.select_one('td:last-child').text.split('重要说明')[0]
    result['wxsx'] = processing_text(tfes, delete_space=True)

    tr2 = trs[1]
    # 农历生日
    gc = tr2.select('td:nth-child(n+2)')
    for i in gc:
        result['birthday']['lc'] += i.text
    tr3 = trs[2]
    # 八字
    for i in tr3.select('td')[1:]:
        result['bz'].append(i.text.strip())

    tr4 = trs[3]
    # 五行
    for i in tr4.select('td')[1:]:
        result['wx'].append(i.text.strip())

    tr5 = trs[4]
    # 纳音
    for i in tr5.select('td')[1:]:
        result['ny'].append(i.text.strip())

    # 八字五行个数
    ecfln = processing_text(tables[1].select_one('tr td').text, ['八字五行个数 : '])
    # 正则开始匹配
    for i in ['金', '木', '水', '火', '土']:
        result['bzwxgs'].append(int(re.search(f'(\d+)个{i}', ecfln).group(1)))

    # 四季用神参考
    result['sjys'] = processing_text(
        tables[2].select_one('tr:first-child td').text, ['四季用神参考 : '], delete_space=True
    )

    # 穷通宝鉴调候用神参考
    result['qtbjdhys'] = processing_text(
        tables[2].select_one('tr:last-child td').text, ['穷通宝鉴调候用神参考 : '], delete_space=True
    )

    # 日干心性
    result['rgxx'] = processing_text(
        tables[3].select_one('tr td:last-child').text, delete_space=True
    )

    # 日干支层次
    result['rgzcs'] = processing_text(
        tables[4].select_one('tr td:last-child').text, delete_space=True
    )

    # 日干支分析
    tables[5].select_one('tr td:last-child font').decompose()
    result['rgzfx'] = processing_text(
        tables[5].select_one('tr td:last-child').text
    )

    trs = tables[6].select('tr')
    # 五行生克制化宜忌
    result['wxskzhyj'] = processing_text(
        trs[0].select_one('td:last-child').text, delete_space=True, line_feed=True
    )

    # 五行之性
    result['wxzx'] = processing_text(
        trs[1].select_one('td:last-child').text, delete_space=True
    )

    # 四柱五行生克中对应需补的脏腑和部位
    result['szwxskxb'] = processing_text(
        trs[2].select_one('td:last-child').text, delete_space=True
    )

    # 宜从事行业与方位
    result['syfw'] = processing_text(
        trs[3].select_one('td:last-child').text, delete_space=True
    )

    # 生肖个性
    sxgx = tables[7].select_one('tr td:last-child')
    url = sxgx.select_one('script').get('src')

    async with aiohttp.ClientSession() as c:
        r = await c.get('http://www.dajiazhao.com/'+url)
    t = re.search('<p>(.+)<a', (await r.text())).group(1)
    em = sxgx.select_one('em')
    emt = em.text
    em.decompose()
    result['sxgx'] = processing_text(
        f'''
        {sxgx.text}

        {t}

        {emt}
        ''', delete_space=True, line_feed=True
    )

    # 三命通会
    result['smth'] = processing_text(
        tables[8].select_one('tr td:last-child').text, delete_space=True, line_feed=True
    )

    # 月日时命理
    trs = tables[9].select('tr')
    y = trs[0].select('td')
    result['yrsml']['y'].append(y[1].text)
    result['yrsml']['y'].append(
        processing_text(y[2].text, delete_space=True, line_feed=True)
    )
    r = trs[1].select('td')
    result['yrsml']['r'].append(r[0].text)
    result['yrsml']['r'].append(
        processing_text(r[1].text, delete_space=True, line_feed=True)
    )
    s = trs[2].select('td')
    result['yrsml']['s'].append(s[0].text)
    result['yrsml']['s'].append(
        processing_text(s[1].text, delete_space=True, line_feed=True)
    )
    # endregion
    return result


replies = {
    'group': {
        'beginning': [
            text('乐意至极，但您真的要在这大庭广众之下做这种事情？')
            + face(0)
            + text('万一算出什么不好的东西怎么办...')
            + face(13),

        ],
        'cancel': [
            text('好吧好吧，如果你还是想算，可以悄悄的来找我哦')
            + face(20) + face(20)
        ],
        'allow': [
            '好吧，那我们开始吧！'
        ]
    },
    'not understand': [
        face(32)
        + text('您在说什么呐，我怎么听不懂呢？')
    ],
    'ln': [
        '您贵姓？',
    ],
    'wrong ln': [
        '请认真一点，这明显就不是一个姓氏！',
        '请不要在这件事上开玩笑！'
    ],
    'fn': [
        '您的名字是什么？不要包括姓氏'
    ],
    'wrong fn': [
        '请认真一点，这明显就不是您的名！',
        '请不要在这件事上开玩笑！'
    ],
    'sex': [
        '您的性别是？'
    ],
    'wrong sex': [
        '不要开玩笑了！您到底是男是女？'
    ],
    'birthday': [
        '请问您是哪一天出生的？公历哦'
    ],
    'wrong birthday': [
        '我无法理解您的生日，请再说一次'
    ],
    'btime': [
        '请问您是{:%Y-%m-%d}几点几分出生的？可以只精确到小时'
    ],
    'wrong btime': [
        '您...这时间不太对啊，请认真一点！'
    ],
    'bt': [
        '好，下一个。您的血型是什么，如果不知道的话请跟我说「不知道」'
    ],
    'wrong bt': [
        '您这，有点不对啊！我所知道的血型只有 A, B, O, AB 四种，您是哪一种？'
    ],
    'confirm': [
        '''请确认您的数据：
姓：「{}」
名：「{}」
性别：「{}」
生日：「{:%Y-%m-%d %H:%M}」
血型：「{}」
请发送「确定」开始，发送「取消」退出'''
    ],
    'cancel':[
        '好吧，您可真无聊。'
    ],
    'getting': [
        '正在帮您进行八字算命...'
    ],
}
msg_false = ['不', '否']
msg_true = ['确定', '当然', '没错', '没关系', '可以', '是']


def has(text, words):
    for i in words:
        if i in text:
            return True
    return False


@ft.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if isinstance(event, GroupMessageEvent):
        await bot.send(
            event, random.choice(replies['group']['beginning'])
        )
    elif isinstance(event, PrivateMessageEvent):
        state['allow'] = True


@ft.got('allow')
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if has(event.raw_message, msg_false):
        await ft.finish(random.choice(replies['group']['cancel']))
    elif has(event.raw_message, msg_true):
        state['allow'] = True
        await bot.send(event, random.choice(replies['group']['allow']))
        await asyncio.sleep(1)
        await bot.send(event, random.choice(replies['ln']))
    else:
        state['allow'] = None
        await ft.reject(random.choice(replies['not understand']))


@ft.got('ln')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    ln = state['ln']
    if not is_all_zh(ln) or 0 == len(ln) or len(ln) > 2:
        await ft.reject(random.choice(replies['wrong ln']))
    else:
        await bot.send(event, random.choice(replies['fn']))


@ft.got('fn')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    fn = state['fn']
    if not is_all_zh(fn) or 0 == len(fn) or len(fn) > 3:
        await ft.reject(random.choice())
    else:
        await bot.send(event, random.choice(replies['sex']))


@ft.got('sex')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    sex = state['sex']
    if sex == '男':
        state['sex'] = 1
    elif sex == '女':
        state['sex'] = 2
    else:
        await ft.reject(random.choice(replies['wrong sex']))
        return
    await bot.send(event, random.choice(replies['birthday']))


@ft.got('birthday')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    birthday = state['birthday']
    rb = re.match('(\d{4})[-./年](\d{1,2})[-./月](\d{1,2})', birthday)
    if rb is None:
        await ft.reject(random.choice(replies['wrong birthday']))
    else:
        state['year'] = int(rb.group(1))
        state['month'] = int(rb.group(2))
        state['day'] = int(rb.group(3))
    await bot.send(
        event, random.choice(
            replies['btime']
        ).format(
            datetime.datetime(state['year'], state['month'], state['day'])
        )
    )


@ft.got('btime')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    btime = state['btime']
    rbt = re.match('(\d{1,2})[点时:](\d{0,2})', btime)
    if rbt is None:
        await ft.reject(random.choice(replies['wrong btime']))
    else:
        state['hour'] = int(rbt.group(1))
        try:
            state['minute'] = int(rbt.group(2))
        except:
            state['minute'] = 0
    await bot.send(event, random.choice(replies['bt']))


@ft.got('bt')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    bt = state['bt']
    if bt == '不知道':
        state['bt'] = ''
    elif bt not in ['A', 'B', 'O', 'AB']:
        await ft.reject(random.choice(replies['wrong bt']))
    await bot.send(
        event,
        random.choice(replies['confirm']).format(
            state['ln'],
            state['fn'],
            '男' if(state['sex'] == 1) else '女',
            datetime.datetime(
                state['year'],
                state['month'],
                state['day'],
                state['hour'],
                state['minute']
            ),
            '未知' if(state['bt']=='') else state['bt']
        )
    )
    await bot.send(event, str(state))

@ft.got('st')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if state['st'] == '取消':
        await ft.finish(random.choice(replies['cancel']))
    elif state['st'] == '确定':
        await bot.send(event, random.choice(replies['getting']))
        return 
        data = (await fortuneTelling(
            state['ln'],
            state['fn'],
            state['sex'],
            datetime.datetime(
                state['year'],
                state['month'],
                state['day'],
                state['hour'],
                state['minute']
            ),
            state['bt']
        ))
        await bot.send(event, str(data))
    else:
        await ft.reject('指令发送有误！')