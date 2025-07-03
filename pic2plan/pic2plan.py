# 我不想写……用支持多模态的大模型吧吧
# 闲的没事可以自己训练一个模型专门识别图片的字体
import base64
import io
import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from PIL import Image

prompt_word = """
请从这张图中获取{group}组的训练计划，按照yaml格式返回，星期的缩写作为key，计划不需要改变原有格式并以多行文本的方式处理，例如
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


# 加载本地图片并转换为 base64 编码
def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


# 将PIL图像对象转为base64
def image_to_base64(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format=image.format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


if __name__ == '__main__':
    model_nme = ''
    api_key = ''
    api_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    group = 'A+'

    image_path = "640.webp"
    image_data = load_image_as_base64(image_path)

    model = ChatOpenAI(
        model_name=model_nme,
        openai_api_key=api_key,
        openai_api_base=api_url
    )
    message = HumanMessage(
        content=json.dumps([
            {"type": "text", "text": prompt_word.replace('{group}', group)},
            {"type": "image", "image": {"data": image_data, "format": "base64"}},
        ])
    )
    response = model.invoke([message])
    print(response.content)
