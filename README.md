# 说明

卢湾跑团训练计划导入佳明（中国区）训练计划

国际区自己改一下域名即可



当前Python版本3.8

- 3.7 parse_plan可以自己改一下
- 3.9 会有警告

## 首次运行

```bash
pip install -r requirements.txt
```

## 配置

### 纯文字文字识别

1. 填写account.json

    ```json
    {
      "username": "这里填账户",
      "password": "这里填密码"
    }
    ```

2. 填写plan.yml

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

   可以只填写一部分

### 大模型图片识别

1. 填写account.json

   ```json
   {
     "username": "这里填账户",
     "password": "这里填密码",
     "group": "这里填组别"
   }
   ```
2. 填写.env文件

    填写自己的配置，推荐qvq-max，每次大概消耗2200tokens
    ```dotenv
    MODEL_NAME=
    BASE_URL=
    API_KEY=
    ```

3. 复制公众号的图片地址

## 使用

```bash
python main.py # 读取plan.yml并同步到佳明
python main.py --debug # 仅读取plan.yml，不同步到佳明
python main.py --pic https://... # 复制公众号的图片链接，调用大模型解析
```

## TODO

- [x] 大模型处理图片
- [ ] 本地OCR