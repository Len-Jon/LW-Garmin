from copy import deepcopy

from .parse import *
from .const import *

WORKOUT_JSON = {
    "sportType": {
        "sportTypeId": 1,
        "sportTypeKey": "running",
        "displayOrder": 1
    },
    "subSportType": None,
    "workoutName": "",  # 填充课程名称
    "estimatedDistanceUnit": {
        "unitKey": None
    },
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {
                "sportTypeId": 1,
                "sportTypeKey": "running",
                "displayOrder": 1
            },
            "workoutSteps": []  # 填充步骤json
        }
    ],
    "avgTrainingSpeed": 0.0,  # 未知参数 置零吧
    "estimatedDurationInSecs": 0,
    "estimatedDistanceInMeters": 0,
    "estimateType": None,
    "isWheelchair": False
}


def create_step_json_repeat(step_id, step_order, child_id, repeat, workout_steps=None, skip=False) -> dict:
    """
    创建一个循环的步骤
    :return: repeat step json
    """
    if workout_steps is None:
        workout_steps = []
    return {
        "stepId": step_id,
        "stepOrder": step_order,
        "stepType": STEP_TYPE_DICT['repeat'],
        "numberOfIterations": repeat,
        "smartRepeat": False,
        "childStepId": child_id,
        "workoutSteps": workout_steps,
        "endCondition": CONDITION_TYPE_DICT['iterations'],
        "type": "RepeatGroupDTO",
        "skipLastRestStep": skip
    }


def create_step_json_workout(step_id, step_order, step_type, end_condition_type, value, target=None, child_id=None,
                             description=None) -> dict:
    """
    创建一个动作的步骤
    :return: workout step json
    """
    step = {
        "stepId": step_id,
        "stepOrder": step_order,
        "stepType": STEP_TYPE_DICT[step_type],
        "type": "ExecutableStepDTO",
        "endCondition": CONDITION_TYPE_DICT[end_condition_type],
        "endConditionValue": value,
        "preferredEndConditionUnit": None,
        "stepAudioNote": None
    }
    if end_condition_type == 'rest':
        step["stepType"] = STEP_TYPE_DICT['rest']
    if end_condition_type == 'distance':
        step["preferredEndConditionUnit"] = {"unitKey": "meter"}
    if target is not None:
        seconds_per_km = str2seconds(target)
        step['targetType'] = TARGET_TYPE_DICT['pace.zone']
        step['targetValueOne'] = 1000 / (seconds_per_km - 10)
        step['targetValueTwo'] = 1000 / (seconds_per_km + 10)
    else:
        step['targetType'] = TARGET_TYPE_DICT['no.target']
    if child_id is not None:
        step['childStepId'] = child_id
    if description is not None:
        step['description'] = description
    return step


def create_workout_steps_json(plan: Union[str, list]) -> list:
    """
    创建单次课程的所有步骤
    :param plan: 单次课程包含的所有步骤文本
    :return: 单次课程的workout steps json
    """
    step_order = 2
    step_id = 4  # 维护步骤ID，好像也不重要，这个是佳明数据库里最后重新赋值的
    child_id = 1  # 维护循环id
    workout_list = [WARMUP_STEP]
    for x in get_step_list(plan):
        if 'repeat' in x:
            running = create_step_json_workout(step_id, step_order + 1, 'interval', 'distance', x['distance'],
                                               x['pace']['km'],
                                               child_id=child_id, description='单圈' + x['pace']['400m'])  # 跑
            rest = create_step_json_workout(step_id + 1, step_order + 2, 'rest', 'time', str2seconds(x['rest']),
                                            child_id=child_id)  # 停
            r = create_step_json_repeat(step_id + 2, step_order, child_id, x['repeat'], [running, rest])  # 循环
            step_id += 3
            step_order += 3
            child_id += 1
            workout_list.append(r)
        else:
            if x.get('distance'):
                t = 'distance'
                v = x['distance']
            else:
                t = 'time'
                v = x['time']
            running = create_step_json_workout(step_id, step_order, 'interval', t, v, x['pace']['km'],
                                               description='单圈' + x['pace']['400m'])
            step_id += 1
            step_order += 1
            workout_list.append(running)
            if 'rest' in x:
                workout_list.append(create_step_json_workout(step_id, step_order, 'rest', 'time', str2seconds(x['rest'])))
                step_id += 1
                step_order += 1
    COOLDOWN_STEP['stepOrder'] = step_order
    workout_list.append(COOLDOWN_STEP)
    return workout_list


def create_workout_json(plan: Union[str, list], workout_name="LW"):
    """
    解析单次课程的文本，创建组装好的课程请求的payload
    :param plan: 单次训练课程的包含的步骤文本
    :param workout_name: 课程名称
    :return: 单次 workout json
    """
    WORKOUT_JSON['workoutSegments'][0]['workoutSteps'] = create_workout_steps_json(plan)
    WORKOUT_JSON['workoutName'] = workout_name
    return deepcopy(WORKOUT_JSON)
