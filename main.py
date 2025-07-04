import argparse
import json

import garth
import yaml

import garmin
import pic2plan.open_ai

parser = argparse.ArgumentParser(description='main')
parser.add_argument("--debug", action="store_true", help="debug模式不发送请求至佳明")
parser.add_argument("--pic", type=str, help="传图图片路径")


def main():
    args = parser.parse_args()
    account = json.load(open("account.json", encoding="utf-8"))
    data_list = []

    if pic_url := args.pic:
        print('[INFO] loading model...')
        plan_txt = pic2plan.open_ai.get_plans(pic_url, account['group'])
    else:
        print('[INFO] loading plan.yml...')
        plan_txt = open('plan.yml', 'r')

    try:
        # 加载 YAML 文件内容
        plan = yaml.safe_load(plan_txt)
        print('[INFO] loaded.')
        for k, v in plan.items():
            if len(v) > 0:
                print(k)
                data_list.append(garmin.create_workout_json(v, 'LW-' + k))
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)
    if args.debug:
        print('[DEBUG] EXIT')
        exit(0)

    cn_username = account['username']
    cn_password = account['password']
    assert cn_username, "username is required"
    assert cn_password, "password is required"
    garth.configure(domain="garmin.cn")
    print('[INFO] Login and post...')
    garth.login(cn_username, cn_password)
    garth.client.sess.headers.update({"User-Agent": "GCM-iOS-5.7.2.1"})
    for data in data_list:
        garth.client.connectapi('/workout-service/workout', "POST", json=data)
    print('[INFO] 完成, 打开Connect-更多训练和计划-训练课程, 选择LW-开头的训练发送至设备')


if __name__ == '__main__':
    main()
