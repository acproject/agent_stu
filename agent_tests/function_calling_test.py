import os
from openai import OpenAI
import json


client  =OpenAI(
    api_key=os.getenv("DeepSeek"),
    base_url="https://api.deepseek.com/v1"
)

# Chat Completions(对话补全) API，它将涉及4个角色：
# system：看成全局变量，约束对话的范围
# user：会话发起人，人类的角色
# assistant：AI助手角色
# tool：工具，调用Function Calling时用到

completion = client.chat.completions.create(

        #set the model to 'deepseek-reasoner'
        model="deepseek-reasoner",
        messages = [
            {'role':'system', 'content':'你是一个足球领域的专家，请针对问题给出简洁的回答。'},
            {'role':'user', 'content':'C罗是哪个国家的足球运动员？'},
            {'role':'assistant', 'content':'C罗是葡萄牙足球运动员。'},
            {'role':'user', 'content':'内马尔呢？'},
            ]

        )

print("### 思考过程： ")
print(completion.choices[0].message.reasoning_content)

print("\n\n")

print("### 最终答案： ")
print(completion.choices[0].message.content)


# 工具的使用
# 对于工具的定义主要有三个字段来完成：
# * name
# * description
# * parameters
#

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_closing_price",
            "description": "使用该工具获取指定股票的收盘价",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "股票名称",}
                    },
                "required":["name"]
            },
        }
    },
]



def send_messages(messages):
    response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
    )
    
    return response


def get_closing_price(name):
    pass



if __name__ == "__main__":
    messages = [{"role":"user", "content":"海天味业的收盘价是多少"}]
    response = send_messages(messages)

    print("回复：")
    print(response.choices[0].message.content)

    print("工具选择：")
    print(response.choices[0].message.tool_calls)

    # 这里是人类调用工具
    messages.append(response.choices[0].message)

    tool_call = response.choices[0].message.tool_calls[0]
    arguments_dict = json.loads(tool_call.function.arguments)
    price = get_closing_price(arguments_dict['name'])
    messages.append({"role":"tool", "content": price, "tool_call_id" : tool_call.id})

    response == send_messages(messages)
    print('回复：')
    print(response.choices[0].message.content)

    # 实现对轮对话
    if response.choices[0].message.tool_calls != None:
        messages.append(response.choices[0].message)

        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "get_closing_price":
                arguments_dict = json.loads(tool_call.function.arguments)
                price = get_closing_price(arguments_dict['name'])

                messages.append({
                    "role": "tool", "content": price, "tool_call_id": tool_call.id
                    })
        response = send_messages(messages)
        print("回复：")
        print(response.choices[0].message.content)

        print("工具选择：")
        print(response.choices[0].message.tool_calls)

        

