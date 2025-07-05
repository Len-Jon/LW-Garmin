import argparse
import json
import urllib3

import garth
import yaml

import garmin
import ocr.open_ai

import sys
from importlib.metadata import version

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='main')
parser.add_argument("--pic", "-p", type=str, help="传入图片路径")
parser.add_argument("--stop_before", "-s", type=str, choices=['garmin', 'g', 'device', 'd'],
                    help="停止位置 默认不指定全部运行 garmin:仅分析计划 device:发送的佳明但不发送到设备")


# 重写 session 的 request 方法，强制加上 verify=False
def patch_request(method):
    orig_request = method

    def new_request(*args, **kwargs):
        kwargs['verify'] = False
        return orig_request(*args, **kwargs)

    return new_request


def main():
    args = parser.parse_args()
    # 载入账户信息
    with open("account.json", "r", encoding="utf-8") as f:
        account = json.load(f)
    # 判断参数 从公众号图片/本地文字获取
    if pic_url := args.pic:
        print('[INFO][0] loading plan from URL by LLM...', flush=True)
        group = account.get('group', '').strip()
        if not group:
            print('\033[93m[WARN][0] 当前调用大模型获取训练计划，但account.json中未配置组别，请补充\033[0m')
            group = input("请输入组别: ").strip()
            account['group'] = group
            with open('account.json', 'w', encoding='utf-8') as f:
                # noinspection PyTypeChecker
                json.dump(account, f, ensure_ascii=False, indent=4)
        plan_txt = ocr.open_ai.get_plans(pic_url, account['group'])
    else:
        print('[INFO][0] loading plan from plan.yml...')
        with open('plan.yml', 'r') as f:
            plan_txt = f.read()
    try:
        # 加载 YAML 格式的计划内容
        plan = yaml.safe_load(plan_txt)
        print('[INFO][0] loaded.')
        data_list = []
        for k, v in plan.items():
            if len(v) > 0:
                print(k)
                data_list.append(garmin.create_workout_json(v, 'LW-' + k))
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

    # 仅解析时此处退出
    if args.stop_before in ['garmin', 'g']:
        print('[INFO][0] EXIT before post to garmin.')
        exit(0)

    print('[INFO][1] Logining in garmin...', flush=True)
    cn_username = account['username']
    cn_password = account['password']
    assert cn_username, "username is required"
    assert cn_password, "password is required"
    garth.configure(domain="garmin.cn")
    garth.client.sess.request = patch_request(garth.client.sess.request)  # 修复一个奇怪的问题

    garth.login(cn_username, cn_password)
    # 一星期一次 早过期了没必要保存
    # garth.save('~/.garth')
    print(f'[INFO][1] Logged in.', flush=True)

    print('[INFO][1] Deleting old workouts...', flush=True)
    for wk in garth.client.connectapi(
            '/workout-service/workouts?start=1&limit=999&myWorkoutsOnly=true&sharedWorkoutsOnly=false&orderBy=WORKOUT_NAME&orderSeq=ASC&includeAtp=false'):
        if wk['workoutName'].startswith('LW-'):
            garth.client.connectapi(f"/workout-service/workout/{wk['workoutId']}", "POST",
                                    headers={'X-HTTP-Method-Override': 'DELETE'})
    print('[INFO][1] Deleted old workouts.', flush=True)

    print('[INFO][1] Creating new workouts...', flush=True)
    workout_id_list = []
    for data in data_list:
        workout_resp = garth.client.connectapi('/workout-service/workout', "POST", json=data)
        if workout_resp is not None:
            workout_id_list.append(workout_resp['workoutId'])
        else:
            print(f'[ERROR][1] {workout_resp}')
    print('[INFO][1] Created workouts.', flush=True)

    if args.stop_before in ['device', 'd']:
        print('[INFO][1] Exit before post to device.')
        exit(0)
    # 检查版本
    garth_version_str = version("garth")
    garth_version = tuple(map(int, garth_version_str.split('.')))
    if sys.version_info < (3, 10) and garth_version < (0, 5):
        print("\033[93m" +
              "[WARN][2] 推送设备功能garth版本需0.5, 0.5以下版本会报错，安装此版本garth需要Python 3.10以上\n" +
              f"当前: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, " +
              f"garth {garth_version_str}\n" +
              "[WARN][2] Exit before post to device."
              "\033[0m")
        exit(1)

    print('[INFO][2] Posting to device.')
    user_profile = garth.UserProfile.get()
    device_id = \
        garth.client.connectapi(f'/device-service/deviceservice/device-info/all/{user_profile.display_name}')[0][
            'baseDeviceDTO']['deviceId']
    # 发送至设备
    garth.client.connectapi('/device-service/devicemessage/messages', "POST",
                            json=garmin.create_message_json(device_id, workout_id_list))
    print('[INFO][2] Posted.')


if __name__ == '__main__':
    main()
