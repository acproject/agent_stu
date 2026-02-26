tools = [
    {
        "name":"get_score_by_name",
        "description":"使用该工具获取指定员工的绩效评分",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "员工姓名",
                }
            },
            "required": ["name"]
        },

    },

    {
        "name":"generating_performance_reviews",
        "description": "根据输入的简单员工评价，生成员工的绩效评语",
        "parameters": {
            "type": "object",
            "properties": {
                "estimation": {
                    "type": "string",
                    "description":"员工的简单评价",
                }
            },
            "required":["estimation"]
        },
    },
]
