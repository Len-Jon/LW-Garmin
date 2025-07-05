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
parser.add_argument("--pic", type=str, help="传入图片路径")
parser.add_argument("--stop_before", type=str, choices=['garmin', 'device'],
                    help="停止位置 默认不指定全部运行 garmin:仅分析计划 device:发送的佳明但不发送到设备")


def main():
    args = parser.parse_args()
    # 载入账户信息
    with open("account.json", "r", encoding="utf-8") as f:
        account = json.load(f)
    # 判断参数 从公众号图片/本地文字获取
    if pic_url := args.pic:
        print('[INFO] loading model...', flush=True)
        plan_txt = ocr.open_ai.get_plans(pic_url, account['group'])
    else:
        print('[INFO] loading plan.yml...')
        with open('plan.yml', 'r') as f:
            plan_txt = f.read()
    try:
        # 加载 YAML 格式的计划内容
        plan = yaml.safe_load(plan_txt)
        print('[INFO] loaded.')
        data_list = []
        for k, v in plan.items():
            if len(v) > 0:
                print(k)
                data_list.append(garmin.create_workout_json(v, 'LW-' + k))
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

    # 仅解析此处退出
    if args.stop_before and args.stop_before == 'garmin':
        print('[INFO] EXIT before post to garmin.')
        exit(0)
    # 检查版本
    garth_version_str = version("garth")
    garth_version = tuple(map(int, garth_version_str.split('.')))
    if garth_version >= (0, 5):
        print("\033[93m" +
              f"[WARN] garth_version {garth_version_str} 此版本可能出现 SSLError, " +
              "如需处理，请修改依赖库中相关文件，以.venv为例" +
              "修改 .venv/lib/python3.10/site-packages/garth/http.py" +
              """
                  self.last_resp = self.sess.request(
                      method,
                      url,
                      headers=headers,
                      timeout=self.timeout,
+                     verify=False,
                      **kwargs,
                  )
                  """ +
              "添加此项参数后可能会有警告，可忽略" +
              "\033[0m")

    print('[INFO] Logining in...', flush=True)
    cn_username = account['username']
    cn_password = account['password']
    assert cn_username, "username is required"
    assert cn_password, "password is required"
    garth.configure(domain="garmin.cn")
    garth.login(cn_username, cn_password)
    # 一星期一次 早过期了没必要保存
    # garth.save('~/.garth')
    print(f'[INFO] Logged in.', flush=True)

    print('[INFO] Deleting old workouts...', flush=True)
    for wk in garth.client.connectapi(
            '/workout-service/workouts?start=1&limit=999&myWorkoutsOnly=true&sharedWorkoutsOnly=false&orderBy=WORKOUT_NAME&orderSeq=ASC&includeAtp=false'):
        if wk['workoutName'].startswith('LW-'):
            garth.client.connectapi(f"/workout-service/workout/{wk['workoutId']}", "POST",
                                    headers={'X-HTTP-Method-Override': 'DELETE'})
    print('[INFO] Deleted old workouts.', flush=True)

    print('[INFO] Creating new workouts...', flush=True)
    workout_id_list = []
    for data in data_list:
        workout_resp = garth.client.connectapi('/workout-service/workout', "POST", json=data)
        if workout_resp is not None:
            workout_id_list.append(workout_resp['workoutId'])
        else:
            print(f'[ERROR] {workout_resp}')
    print('[INFO] Created workouts.', flush=True)

    if args.stop_before == 'device':
        print('[INFO] Exit before post to device.')
        exit(0)
    if sys.version_info < (3, 10) and garth_version < (0, 5):
        print("\033[93m" +
              "[WARN] 推送设备功能garth版本需0.5以下版本会报错，安装此版本garth需要Python 3.10以上\n" +
              f"当前: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, " +
              f"garth {garth_version_str}"
              "\033[0m")
        print("[INFO] Exit before post to device.")
        exit(1)

    print('[INFO] Posting to device.')
    user_profile = garth.UserProfile.get()  # 0.5.0才修复，但是这个要求python3.10，懒得更新
    device_id = \
        garth.client.connectapi(f'/device-service/deviceservice/device-info/all/{user_profile.display_name}')[0][
            'baseDeviceDTO']['deviceId']
    # 发送至设备
    garth.client.connectapi('/device-service/devicemessage/messages', "POST",
                            json=garmin.create_message_json(device_id, workout_id_list))
    print('[INFO] Posted.')


if __name__ == '__main__':
    main()
