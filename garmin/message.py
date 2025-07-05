from copy import deepcopy


def create_single_message(device_id: int, workout_id: int) -> dict:
    return {
        "deviceId": device_id,
        "messageUrl": f"workout-service/workout/FIT/{workout_id}",
        "messageType": "workouts",
        "messageName": "LW-Thu",
        "groupName": None,
        "priority": 1,
        "fileType": "FIT",
        "metaDataId": workout_id
    }


def create_message_json(device_id: int, workout_id_list: list) -> list:
    """
    获取推送的的payload
    :param device_id: 设备id
    :param workout_id_list: 课程idList
    :return: payload
    """
    return deepcopy([create_single_message(device_id, x) for x in workout_id_list])
