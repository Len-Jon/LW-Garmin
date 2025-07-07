# 步骤类型
STEP_TYPE_DICT = {
    "warmup": {
        "stepTypeId": 1,
        "stepTypeKey": "warmup",
        "displayOrder": 1
    },
    "cooldown": {
        "stepTypeId": 2,
        "stepTypeKey": "cooldown",
        "displayOrder": 2
    },
    "interval": {
        "stepTypeId": 3,
        "stepTypeKey": "interval",
        "displayOrder": 3
    },
    "recovery": {
        "stepTypeId": 4,
        "stepTypeKey": "recovery",
        "displayOrder": 4
    },
    "rest": {
        "stepTypeId": 5,
        "stepTypeKey": "rest",
        "displayOrder": 5
    },
    "repeat": {
        "stepTypeId": 6,
        "stepTypeKey": "repeat",
        "displayOrder": 6
    }
}
# 目标类型，通常只有配速目标
TARGET_TYPE_DICT = {
    "no.target": {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1
    },
    "pace.zone": {
        "workoutTargetTypeId": 6,
        "workoutTargetTypeKey": "pace.zone",
        "displayOrder": 6
    }
}
# 判断完成类型 通常只有时间和距离两种，组循环另外判断
CONDITION_TYPE_DICT = {
    "time": {
        "conditionTypeId": 2,
        "conditionTypeKey": "time",
        "displayOrder": 2,
        "displayable": True
    },
    "distance": {
        "conditionTypeId": 3,
        "conditionTypeKey": "distance",
        "displayOrder": 3,
        "displayable": True
    },
    "iterations": {
        "conditionTypeId": 7,
        "conditionTypeKey": "iterations",
        "displayOrder": 7,
        "displayable": False
    },
}

WARMUP_STEP = {
    "stepId": 1,
    "stepOrder": 1,
    "stepType": {
        "stepTypeId": 1,
        "stepTypeKey": "warmup",
        "displayOrder": 1
    },
    "type": "ExecutableStepDTO",
    "endCondition": {
        "conditionTypeId": 1,
        "conditionTypeKey": "lap.button",
        "displayOrder": 1,
        "displayable": True
    },
    "endConditionValue": 1000,
    "targetType": {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1
    }
}

COOLDOWN_STEP = {
    "stepId": 3,
    "stepOrder": 7,
    "stepType": {
        "stepTypeId": 2,
        "stepTypeKey": "cooldown",
        "displayOrder": 2
    },
    "type": "ExecutableStepDTO",
    "endCondition": {
        "conditionTypeId": 1,
        "conditionTypeKey": "lap.button",
        "displayOrder": 1,
        "displayable": True
    },
    "endConditionValue": 1000,
    "targetType": {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1
    }
}
