import os
from openai import OpenAI
from registed_tools import tools as registered_tools

client  =OpenAI(
    api_key=os.getenv("DeepSeek"),
    base_url="https://api.deepseek.com/v1"
)

openai_tools = [{"type": "function", "function": tool} for tool in registered_tools]


def get_score_by_name(name):
    # 真实的情况是通过数据库查询到数据后返回，下面的是测试用用例代码：
    if name == "张三":
        return "name:张三 绩效评分:85.9"
    elif name == "李四":
        return "name:李四 绩效评分:92.7"
    else:
        return "未查到该员工的绩效"


def generating_performance_reviews(estimation):
    completion = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {'role' :'system', 'content': '你是一个公司的领导，请根据我给你的员工的额简单评价，生成一段50字左右的评语'},
            {'role': 'user', 'content': estimation},
        ]
    )
    return completion.choices[0].message.content


def send_messages(messages):
    response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
    )
    
    return response
