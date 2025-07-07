import argparse
import json
import os
import sys
from importlib.metadata import version
from typing import Any, List

import garth
import urllib3
import yaml

import garmin
import ocr.open_ai

# 禁用 SSL 警告
urllib3.disable_warnings()

# 全局常量，此处也可以填入图片URL，需要调用LLM解析可空值调用--pic/-p
DEFAULT_PIC_URL = ''

LOG_PREFIXES = {
    'INFO': '\033[92m[INFO]\033[0m',
    'WARN': '\033[93m[WARN]\033[0m',
    'ERROR': '\033[91m[ERROR]\033[0m'
}

# 获取当前脚本所在的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_JSON = os.path.join(CURRENT_DIR, 'account.json')
PLAN_YML = os.path.join(CURRENT_DIR, 'plan.yml')


# 配置参数解析器
def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='训练计划同步脚本')
    parser.add_argument("--pic", "-p", const=DEFAULT_PIC_URL, nargs='?', type=str,
                        help="解析图片中的训练计划，传入图片路径或URL")
    parser.add_argument("--stop_before", "-s", type=str,
                        choices=['garmin', 'g', 'device', 'd'],
                        help="指定停止位置: garmin(仅分析) | device(发送到Garmin不发设备)")
    parser.add_argument("--ps", '-ps', type=str, choices=['garmin', 'g', 'device', 'd'])
    return parser


# 日志打印函数
def log(level: str, message: str):
    prefix = LOG_PREFIXES.get(level.upper(), "")
    print(f"{prefix} {message}", flush=True)


# 补充空 pic 输入
def handle_missing_pic(args: argparse.Namespace) -> None:
    if args.pic is not None and not args.pic.strip():
        log("WARN", "[0] 指定了--pic/-p，但PIC_URL为空，请补充")
        user_input = input("请输入图片地址: ").strip()
        if not user_input:
            log("ERROR", "输入不能为空，程序退出。")
            sys.exit(1)
        args.pic = user_input


# 加载 account.json
def load_account() -> dict:
    try:
        with open(ACCOUNT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log("ERROR", f"加载 {ACCOUNT_JSON} 失败: {e}")
        sys.exit(1)


# 保存组别信息
def save_group_to_account(account: dict, group: str) -> None:
    account['group'] = group
    try:
        with open(ACCOUNT_JSON, 'w', encoding='utf-8') as f:
            json.dump(account, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log("ERROR", f"写入 {ACCOUNT_JSON} 失败: {e}")
        sys.exit(1)


# 获取训练计划文本
def get_plan_text(args: argparse.Namespace, account: dict) -> str:
    pic_url = args.pic
    if pic_url:
        log("INFO", "[0] Loading plan from URL by LLM...")
        group = account.get('group', '').strip()
        if not group:
            log("WARN", "[0] 当前调用大模型获取训练计划，但account.json中未配置组别，请补充")
            group = input("请输入组别: ").strip()
            save_group_to_account(account, group)
        try:
            return ocr.open_ai.get_plans(pic_url, group)
        except Exception as e:
            log("ERROR", f"[0] OCR 解析失败: {e}")
            sys.exit(1)
    else:
        log("INFO", f"[0] Loading plan from {PLAN_YML}...")
        try:
            with open(PLAN_YML, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            log("ERROR", f"{PLAN_YML} 文件未找到: {e}")
            sys.exit(1)


# 解析并生成所有 workout json 数据
def parse_plan(plan_txt: str) -> List[Any]:
    try:
        plan_yml = yaml.safe_load(plan_txt)
        workout_list = []
        for k, v in plan_yml.items():
            if len(v) > 0:
                print(k)
                workout_list.append(garmin.create_workout_json(v, 'LW-' + k))
        return workout_list
    except yaml.YAMLError as exc:
        log("ERROR", f"YAML 解析失败: {exc}")
        sys.exit(1)


# 修复SSL Error警告
def init_garth() -> None:
    garth.configure(domain="garmin.cn")

    # 修复 garth 的 request 方法
    def patch_request(method):
        def new_request(*args, **kwargs):
            kwargs['verify'] = False
            return method(*args, **kwargs)

        return new_request

    garth.client.sess.request = patch_request(garth.client.sess.request)


# 登录 Garmin
def login_garmin(account: dict) -> None:
    cn_username = account.get('username')
    cn_password = account.get('password')
    if not cn_username or not cn_password:
        log("ERROR", "账号密码缺失，请检查 account.json")
        sys.exit(1)

    log("INFO", "[1] Logining in garmin...")
    garth.login(cn_username, cn_password)
    log("INFO", "[1] Logged in.")


# 删除旧 workout
def delete_old_workouts():
    log("INFO", "[1] Deleting old workouts...")
    try:
        for wk in garth.client.connectapi(
                '/workout-service/workouts?start=1&limit=999&myWorkoutsOnly=true&sharedWorkoutsOnly=false&orderBy=WORKOUT_NAME&orderSeq=ASC&includeAtp=false'
        ):
            if wk['workoutName'].startswith('LW-'):
                garth.client.connectapi(
                    f"/workout-service/workout/{wk['workoutId']}",
                    "POST",
                    headers={'X-HTTP-Method-Override': 'DELETE'}
                )
        log("INFO", "[1] Deleted old workouts.")
    except Exception as e:
        log("ERROR", f"[1] 删除旧数据失败: {e}")


# 将解析的训练课程推送到佳明
def post_to_garmin(workout_json_list: list) -> list:
    log("INFO", "[1] Creating new workouts...")
    workout_id_list = []
    for workout_json in workout_json_list:
        try:
            workout_resp = garth.client.connectapi('/workout-service/workout', "POST", json=workout_json)
            if workout_resp:
                workout_id_list.append(workout_resp['workoutId'])
            else:
                log("ERROR", f"[1] 创建 Workout 失败: {workout_resp}")
        except Exception as e:
            log("ERROR", f"[1] 创建 Workout 失败: {e}")
    log("INFO", "[1] Created workouts.")
    return workout_id_list


# 推送至设备
def post_to_device(workout_id_list: list):
    log("INFO", "[2] Posting to device.")
    try:
        user_profile = garth.UserProfile.get()
        device_id = garth.client.connectapi(
            f'/device-service/deviceservice/device-info/all/{user_profile.display_name}'
        )[0]['baseDeviceDTO']['deviceId']
        garth.client.connectapi(
            '/device-service/devicemessage/messages',
            "POST",
            json=garmin.create_message_json(device_id, workout_id_list)
        )
        log("INFO", "[2] Posted.")
    except Exception as e:
        log("ERROR", f"[2] 推送设备失败: {e}")


# 主函数
def main():
    parser = configure_parser()
    args = parser.parse_args()

    if args.ps is not None:
        args.stop_before = args.ps.strip()
        args.pic = DEFAULT_PIC_URL

    handle_missing_pic(args)
    account = load_account()
    plan_txt = get_plan_text(args, account)

    try:
        workout_json_list = parse_plan(plan_txt)
        if len(workout_json_list) == 0:
            log("WARN", "计划列表为空，请检查输入源plan.yml或pic_url是否有效")
    except Exception as e:
        log("ERROR", f"请检查输入源plan.yml或pic_url是否有效")
        sys.exit(1)

    if args.stop_before in ['garmin', 'g']:
        log("INFO", "[0] EXIT before post to garmin.")
        sys.exit(0)

    init_garth()
    login_garmin(account)
    delete_old_workouts()
    workout_id_list = post_to_garmin(workout_json_list)

    if args.stop_before in ['device', 'd']:
        log("INFO", "[1] Exit before post to device.")
        sys.exit(0)

    # 检查版本兼容性
    garth_version_str = version("garth")
    garth_version = tuple(map(int, garth_version_str.split('.')))
    if garth_version < (0, 5):
        log("WARN",
            f"[2] 推送设备功能garth需 >=0.5, 此版本要求Python需 >=3.10, 当前 garth {garth_version_str}")
        sys.exit(1)

    post_to_device(workout_id_list)


if __name__ == '__main__':
    main()
