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


def get_step(line: str) -> dict:
    """
    单行训练步骤文本的结构化
    :param line: 单行结构化训练步骤
    :return: 返回结构化的单个步骤
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


def get_step_list(src: Union[str, list]) -> list:
    """
    拆分单次课程的步骤文本并结构化
    :param src: 多行训练步骤文本
    :return: 结构化的步骤列表
    """
    if type(src) is str:
        return [r for x in src.split('\n') if (r := get_step(x))]
    else:
        return [r for x in src if (r := get_step(x)) and r.keys()]
