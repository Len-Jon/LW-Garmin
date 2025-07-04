import base64

import httpx
from openai import OpenAI, BadRequestError
from .prompt import get_prompt
import os


def get_plans(pic_url: str, group: str) -> str:
    # 初始化OpenAI客户端
    client = OpenAI(
        # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )

    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""  # 定义完整回复
    is_answering = False  # 判断是否结束思考过程并开始回复

    # 创建聊天完成请求
    try:
        completion = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": pic_url
                            },
                        },
                        {"type": "text", "text": get_prompt(group)},
                    ],
                },
            ],
            stream=True,
            # 解除以下注释会在最后一个chunk返回Token使用量
            stream_options={
                "include_usage": True
            }
        )
    except BadRequestError as e:
        print('[WARN]', e)
        print('[WARN] 尝试下载图片后上传...')
        image_data = base64.b64encode(httpx.get(pic_url).content).decode("utf-8")
        completion = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                        {"type": "text", "text": get_prompt(group)},
                    ],
                },
            ],
            stream=True,
            # 解除以下注释会在最后一个chunk返回Token使用量
            stream_options={
                "include_usage": True
            }
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
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                # 打印回复过程
                if delta.content is not None:
                    print(delta.content, end='', flush=True)
                    answer_content += delta.content
    # print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
    # print(reasoning_content)
    # print("=" * 20 + "完整回复" + "=" * 20 + "\n")
    return answer_content.replace("```", "").replace("yaml","")
