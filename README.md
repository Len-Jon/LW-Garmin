# 说明

卢湾跑团训练计划导入佳明（中国区）训练计划

国际区自己改一下域名即可

当前Python版本3.9

当前支持

- [x] 手动输入识别
- [x] 大模型图片识别（需要自己配置api_key）
- [ ] 表格识别
- [ ] 本地OCR识别

## 首次运行

安装依赖

```bash
pip install -r requirements.txt
```

## 佳明账户信息填写

填写`account.json`

```json
{
  "username": "必填-这里填账户",
  "password": "必填-这里填密码",
  "group": "可选-这里填组别，调用大模型识别时会选取"
}
```

例如

```json
{
  "username": "wwqkbb@qq.com",
  "password": "garmin_password",
  "group": "A+"
}
```

# 使用方式

## 1 配置

### 1.1 手动输入识别

1. 按以下方式填写`plan.yml`

    ```yaml
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
    ```

    可以只填写一部分，例如

    ```yaml
    Tue: |
      400@1'20"[1'30"R]*8
      800@1'22"[2'R]*4
      1200@1'24"[3'R]*2
    ```

### 1.2 大模型图片识别

1. 填写.env文件或配置环境变量

    填写自己的配置
    ```dotenv
    MODEL_NAME=
    BASE_URL=
    API_KEY=
    ```

    例如

    ```dotenv
    MODEL_NAME=qwen-vl-plus
    BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
    #API_KEY=sk-000
    ```

    > 比较好用的模型推荐：
    >
    > - [大模型服务平台百炼控制台](https://bailian.console.aliyun.com/?tab=model#/model-market?capabilities=["IU"]&z_type_={"capabilities"%3A"array"})：图片理解的模型基本都行
    > - [Moonshot AI - 开放平台](https://platform.moonshot.cn/docs/introduction)：名字带vision的都能用，但是preview版本不一定保留，可以换别的
    >
    > 并非越精确越好，比如qwen-vl-max肯定要比qwen-vl-plus要更精确的，但后者秒出结果，尤其是qvq-max，消耗token还多几百，思考过程还不能跳过。

2. 复制公众号的图片地址，执行命令时粘贴

## 2 执行命令和参数

- `--debug`：指定此参数时仅查看计划的解析结果，不同步至佳明
- `--pic`：指定此参数时将访问链接中的图片，若不指定则默认识别手动输入的`plan.yml`

```bash
python main.py # 读取plan.yml并同步到佳明
python main.py --debug # 仅读取plan.yml，不同步到佳明
python main.py --pic https://... # 传入公众号的图片链接，调用大模型解析，并同步到佳明
python main.py --debug # 传入公众号的图片链接，仅调用大模型解析，不同步到佳明
```

如果大模型识别不准确（周日的长距离`'`识别成`"`），返回的结果可以复制到plan.yml自己手动调整一下

