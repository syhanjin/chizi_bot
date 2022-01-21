import re

# 连续的空格
multiple_spaces = re.compile(' +')

def list_to_string(strings: 'list | tuple') -> str:
    """
    将列表合成为文本
    :param strings: 文本
    """
    result = ''
    for i in strings:
        result += i + ' '
    return result


def linefeed(string: 'str | tuple | list', length: int) -> str:
    """
    将文本按照指定长度换行
    :param string: 文本
    :param length: 长度
    """
    if type(string) == type((0,)) or type(string) == type([]):
        string = list_to_string(string)
    return re.sub(
        '(.{'+str(length)+'}[，。？！]?)',
        (lambda i: i.group(0)+'\n'),
        string
    )



def space_multiple_to_one(string: str) -> str:
    """
    将文本中连续的空格合成一个
    :param string: 文本
    """
    return multiple_spaces.sub(' ', string).strip()


def delete_space(string: str) -> str:
    """
    删除文本中包括换行符在内的所有空格
    :param string: 文本
    """
    replaces = [' ', '\r', '\n']
    for i in replaces:
        string = string.replace(i, '')
    return string