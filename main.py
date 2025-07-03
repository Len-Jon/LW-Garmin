import json
from copy import deepcopy
from datetime import datetime
import garth
from garmin import workout


def main():
    # import locale
    # locale.setlocale(locale.LC_TIME, 'C.UTF-8')

    # wn = 'LW-TUE'
    # wn = 'LW-THU'
    # wn = 'LW-SUN'
    wn = 'LW-' + datetime.now().strftime("%a")

    with open('plan.txt', encoding="utf-8") as f:
        plan = f.read()
    data = workout.create_workout_json(plan, wn)

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
        cn_client.connectapi('/workout-service/workout', "POST", json=data)
        print('完成, 打开Connect-更多训练和计划-训练课程, 选择LW-开头的训练发送至设备')
    else:
        exit(0)


if __name__ == '__main__':
    main()
