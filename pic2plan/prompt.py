prompt_word = """
1. 定位{group}组在图中表格里的位置。
2. 分别提取周二、周四、周日的计划内容，不包含时间地点类型信息。
3. 按照yaml格式组织数据，使用星期缩写作为键。
4. 计划内容作为值，不改变原有格式，确保多行文本保持原样。
5. 回答以纯文本方式返回，不添加任何解释性文字，不使用包括Markdown在内任何样式。
参考样式：

Tue: |
  400@1'20"[1'30"R]*8
  800@1'22"[2'R]*4
# 以此类推
"""


def get_prompt(group: str) -> str:
    assert group, "group is required"
    return prompt_word.replace('{group}', group)
