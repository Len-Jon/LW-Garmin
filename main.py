import json
from copy import deepcopy

import garth
import yaml

import garmin


def main():
    dataList = []
    with open('plan.yaml', 'r') as config_file:
        try:
            # 加载 YAML 文件内容
            plan = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc)
        for k,v in plan.items():
            if len(v) > 0:
                print(k)
                dataList.append(deepcopy(garmin.create_workout_json(v, 'LW-' + k)))
    x = input('确认计划是否正确，发送至CONNECT输入1，否则取消发送\n')
    if x == '1':
        account = json.load(open("account.json", encoding="utf-8"))
        cn_username = account['username']
        cn_password = account['password']
        assert cn_username, "username is required"
        assert cn_password, "password is required"
        garth.configure(domain="garmin.cn")
        garth.login(cn_username, cn_password)
        cn_client = deepcopy(garth.client)
        cn_client.sess.headers.update({"User-Agent": ("GCM-iOS-5.7.2.1")})
        for data in dataList:
            cn_client.connectapi('/workout-service/workout', "POST", json=data)
        print('完成, 打开Connect-更多训练和计划-训练课程, 选择LW-开头的训练发送至设备')
    else:
        print('取消...')
        exit(0)


if __name__ == '__main__':
    main()
