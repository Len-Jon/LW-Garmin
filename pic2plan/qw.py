from openai import OpenAI
import os
prompt_word = """
请从这张图中获取A2组的训练计划，按照yaml格式返回，星期的缩写作为key，计划不需要改变原有格式并以多行文本的方式处理，例如
Tue: |
  400@1'20"[1'30"R]*8
  800@1'22"[2'R]*4
  1200@1'24"[3'R]*2

Thu: |
  2K@4'20"
  6K@4'10"[3'R]
  4K@3'50"[3'R]
  2K@3'40"

Sun: |
  90'@4'10"
"""
# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
    api_key = "",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

reasoning_content = ""  # 定义完整思考过程
answer_content = ""     # 定义完整回复
is_answering = False   # 判断是否结束思考过程并开始回复

# 创建聊天完成请求
completion = client.chat.completions.create(
    model="qvq-max",  # 此处以 qvq-max 为例，可按需更换模型名称
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/OsnnrVAkYsxzpsX4ETexRyZJdl1SUfiazkZ2lXyZ0iacMYCz7YmZX5P2hINsM3u8AcWClqb2uiaAW3dMUUhdxd0jw/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1"
                    },
                },
                {"type": "text", "text": prompt_word},
            ],
        },
    ],
    stream=True,
    # 解除以下注释会在最后一个chunk返回Token使用量
    # stream_options={
    #     "include_usage": True
    # }
)

print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    # 如果chunk.choices为空，则打印usage
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
    else:
        delta = chunk.choices[0].delta
        # 打印思考过程
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
        else:
            # 开始回复
            if delta.content != "" and is_answering is False:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            # 打印回复过程
            print(delta.content, end='', flush=True)
            answer_content += delta.content

# print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
# print(reasoning_content)
# print("=" * 20 + "完整回复" + "=" * 20 + "\n")
# print(answer_content)