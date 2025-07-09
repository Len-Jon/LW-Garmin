TAG_LIST = [
    {
        "tagId": 9568,
        "title": "轻松跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9569,
        "title": "马拉松配速跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9570,
        "title": "乳酸阈跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9571,
        "title": "间歇跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9572,
        "title": "重复跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9573,
        "title": "节奏跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9574,
        "title": "LSD",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9575,
        "title": "跑力测试",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9576,
        "title": "力量训练",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9577,
        "title": "有氧耐力",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9578,
        "title": "无氧耐力",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9579,
        "title": "燃脂跑",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9580,
        "title": "有氧训练",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9581,
        "title": "无氧训练",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9582,
        "title": "高强度训练",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    },
    {
        "tagId": 9583,
        "title": "耐力训练",
        "tagUsage": "WORKOUT",
        "activityType": "RUNNING"
    }
]
TAG_DICT = {item['title']: item for item in TAG_LIST}
WEEKDAY_TAG_DICT = {
    'TUE': '间歇跑',
    'THU': '节奏跑',
    'SUN': 'LSD'
}


def get_tag_by_weekday(weekday: str) -> dict:
    return TAG_DICT[WEEKDAY_TAG_DICT.get(weekday.upper(), '有氧训练')]
