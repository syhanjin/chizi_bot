
from nonebot.adapters.cqhttp.message import MessageSegment as ms


def welcome_card(text: str, icon: str = '', tips: list = [], buttons: list = []):
    '''
    text: str, 欢迎语

    icon: str, 图标的网址

    tips: list, 元素为一个 元组: (text, [title])
    - text: 提示文本, 标题默认为 温馨提示
    - title: 当添加该值且不为空，则标题将被覆盖

    buttons: list，元素为一个 元组: (name, action)
    - name:   按钮内容
    - action: 按钮所需跳转的网址

    **请注意在单元素元组中添加`,`以消除歧义**
    '''
    proc_tips, proc_btns = [], []
    if tips:
        for i in tips:
            title = '温馨提示'
            try:
                title = i[1] or title
            except:
                pass
            proc_tips.append({
                'value': i[0],
                'title': title
            })
    if buttons:
        for i in buttons:
            proc_btns.append({
                'name': i[0],
                'action': i[1]
            })
    return ms.json({
        "app": "com.tencent.miniapp",
        "desc": "",
        "view": "notification",
        "ver": "0.0.0.1",
        "prompt": "入群欢迎",
        "meta": {
            "notification": {
                "appInfo": {
                    "appName": text,
                    "appType": 4,
                    "appid": 1234567890,
                    "iconUrl": icon
                },
                "data": proc_tips,
                "title": "",
                "button": proc_btns,
                "emphasis_keyword": ""
            }
        }
    })
