from copy import deepcopy

from .parse import *
from .type_dict import *

workout_json = {
    "sportType": {
        "sportTypeId": 1,
        "sportTypeKey": "running",
        "displayOrder": 1
    },
    "subSportType": None,
    "workoutName": "",  # !
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
            "workoutSteps": []  # !
        }
    ],
    "avgTrainingSpeed": 0.0,
    "estimatedDurationInSecs": 0,
    "estimatedDistanceInMeters": 0,
    "estimateType": None,
    "isWheelchair": False
}


def create_repeat(step_id, step_order, child_id, repeat, workout_steps=None, skip=False):
    if workout_steps is None:
        workout_steps = []
    return {
        "stepId": step_id,
        "stepOrder": step_order,
        "stepType": step_type_dict['repeat'],
        "numberOfIterations": repeat,
        "smartRepeat": False,
        "childStepId": child_id,
        "workoutSteps": workout_steps,
        "endCondition": condition_type_dict['iterations'],
        "type": "RepeatGroupDTO",
        "skipLastRestStep": skip
    }


def create_step(step_id, step_order, step_type, end_condition_type, value, target=None, child_id=None,
                description=None):
    step = {
        "stepId": step_id,
        "stepOrder": step_order,
        "stepType": step_type_dict[step_type],
        "type": "ExecutableStepDTO",
        "endCondition": condition_type_dict[end_condition_type],
        "endConditionValue": value,
        "preferredEndConditionUnit": None,
        "stepAudioNote": None
    }
    if end_condition_type == 'rest':
        step["stepType"] = step_type_dict['rest']
    if end_condition_type == 'distance':
        step["preferredEndConditionUnit"] = {"unitKey": "meter"}
    if target is not None:
        seconds_per_km = str2seconds(target)
        step['targetType'] = target_type_dict['pace.zone']
        step['targetValueOne'] = 1000 / (seconds_per_km - 10)
        step['targetValueTwo'] = 1000 / (seconds_per_km + 10)
    else:
        step['targetType'] = target_type_dict['no.target']
    if child_id is not None:
        step['childStepId'] = child_id
    if description is not None:
        step['description'] = description
    return step


def create_workout_steps(plan: Union[str, list]) -> list:
    step_order = 2
    step_id = 4  # 维护步骤ID，好像也不重要，这个是佳明数据库里最后重新赋值的
    child_id = 1  # 维护循环id
    workout_list = [warmup_step]
    for x in parse_plans(plan):
        if 'repeat' in x:
            running = create_step(step_id, step_order + 1, 'interval', 'distance', x['distance'], x['pace']['km'],
                                  child_id=child_id, description='单圈' + x['pace']['400m'])  # 跑
            rest = create_step(step_id + 1, step_order + 2, 'rest', 'time', str2seconds(x['rest']),
                               child_id=child_id)  # 停
            r = create_repeat(step_id + 2, step_order, child_id, x['repeat'], [running, rest])  # 循环
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
            running = create_step(step_id, step_order, 'interval', t, v, x['pace']['km'],
                                  description='单圈' + x['pace']['400m'])
            step_id += 1
            step_order += 1
            workout_list.append(running)
            if 'rest' in x:
                workout_list.append(create_step(step_id, step_order, 'rest', 'time', str2seconds(x['rest'])))
                step_id += 1
                step_order += 1
    cooldown_step['stepOrder'] = step_order
    workout_list.append(cooldown_step)
    return workout_list


def create_workout_json(plan: str, workout_name="LW"):
    """
    获取创建课程请求的payload
    :param plan: 单次workout的原始模式
    :param workout_name: 课程名称
    :return: payload
    """
    workout_json['workoutSegments'][0]['workoutSteps'] = create_workout_steps(plan)
    workout_json['workoutName'] = workout_name
    return deepcopy(workout_json)
