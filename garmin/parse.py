import re
from typing import Union


def str2seconds(src: str) -> int:
    time_pattern = re.compile(r'(\d+)\'(?:(\d+?)")?')
    min_part, seconds_part = re.match(time_pattern, src).groups()
    temp_time = int(min_part) * 60
    if seconds_part:
        temp_time += int(seconds_part)
    return temp_time


def seconds2str(src: (int, float)) -> str:
    return f"{int(src // 60)}'{int(src % 60)}\""


def parse_plan(line: str) -> dict:
    """
    :param line: 单行处理
    :return: 返回结构化的训练描述
    """
    line = line.strip().replace(' ', '')
    line = re.sub(r'[‘’]', "'", line)
    line = re.sub(r'[“”]', '"', line)
    match = re.match(r'([^@]+)@([^\[]+)(?:\[(.*?)R])?\*?(\d+)?', line)
    if not match:
        return {}
    target, pace_str, rest, repeat = match.groups()
    plan = {'distance': '', 'time': '', 'pace': {}}
    # target and pace
    if str.endswith(target, "\'"):
        plan['time'] = str2seconds(target)
        plan['pace']['km'] = pace_str
    elif str.endswith(target, "K"):
        plan['distance'] = int(target.replace('K', '000'))
        plan['pace']['km'] = pace_str
    else:
        plan['distance'] = int(target)
        plan['pace']['km'] = seconds2str(str2seconds(pace_str) * 2.5)
    plan['pace']['400m'] = seconds2str(str2seconds(plan['pace']['km']) / 2.5)
    if rest is not None:
        plan['rest'] = rest
    if repeat is not None:
        plan['repeat'] = int(repeat)
    print(f"  {line:25} 圈速 {plan['pace']['400m']}")
    return plan


# Python 3.8及以上可用，3.7以下自己改改
def parse_plans(src: Union[str, list]) -> list:
    """
    :param src: 原始计划字符串或列表
    :return: 结构化计划列表
    """
    if type(src) is str:
        return [r for x in src.split('\n') if (r := parse_plan(x))]
    else:
        return [r for x in src if (r := parse_plan(x)) and r.keys()]
