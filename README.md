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
     "password": "这里填组别"
   }
   ```

   如果需要使用大模型，

2. 填写plan.txt

   ```
   ```

   

### 大模型图片识别

1. 填写account.json

   ```json
   {
     "username": "这里填账户",
     "password": "这里填组别",
     "model": {
       "modelName": "模型名称"
     }
   }
   ```

2. 复制公众号的图片

## 使用

```bash
python main.py
```

## TODO

- [ ] 本地OCR
- [ ] 