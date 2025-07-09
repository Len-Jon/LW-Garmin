import time

import garth

from . import tags

SPORTS_BASE_URL = f'https://sports.garmin.cn'


# 全程依赖garth登陆后的状态
# 登录佳速度
def login_sports():
    # 获取SESSION->重定向SSO->带ticket重定向回来获取获取登录态
    garth.client.sess.get(SPORTS_BASE_URL)
    # 确认可用性，否则无法刷新权限
    r = garth.client.sess.get(SPORTS_BASE_URL + '/p/appvariable?_=' + str(int(round(time.time() * 1000))))
    r.raise_for_status()
    if r.json()['user']['gccUserId'] == -1:
        raise RuntimeError('Login Garmin Sports Error.')
    return r.json()


from copy import deepcopy


def post_to_sports(payload):
    data = {
        'description': "",
        'workoutName': payload['workoutName'],
        'sportType': payload['sportType'],
        'workoutSegments': payload['workoutSegments'],
        'tagDto': tags.get_tag_by_weekday(payload['workoutName'].split('-')[1])
    }
    print(data)
    r = garth.client.sess.post(SPORTS_BASE_URL + '/proxy/workout-service/workout', json=data)
    print(r.text)
    return r
