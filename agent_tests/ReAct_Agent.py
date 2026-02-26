from tools import get_score_by_name, generating_performance_reviews, send_messages
from registed_tools import tools
import json
import re
from pathlib import Path

REACT_PROMPT = (Path(__file__).resolve().parent / "prompt" / "ReAct_template01.md").read_text(encoding="utf-8")

query = "请比较张三和李四的绩效谁好？并给予绩效较好的员工以赞扬得到绩效评价，给予绩效差一点的员工以鼓励大的绩效评价"
prompt = REACT_PROMPT.replace("{tools}", json.dumps(tools)).replace("{input}", query)

messages = [{"role":"user", "content":prompt}]

while True:
    response = send_messages(messages)
    assistant_message = response.choices[0].message
    response_text = assistant_message.content or ""

    print("大模型的回复： ")
    print(response_text)

    final_answer_match = re.search(r'Final Answer:\s*(.*)', response_text)
    if final_answer_match:
        final_answer = final_answer_match.group(1)
        print("最终答案：", final_answer)
        break


    if assistant_message.tool_calls:
        messages.append(assistant_message)
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            params = json.loads(tool_call.function.arguments or "{}")

            observation = ""
            if tool_name == "get_score_by_name":
                observation = get_score_by_name(params["name"])
            elif tool_name == "generating_performance_reviews":
                observation = generating_performance_reviews(params["estimation"])

            messages.append(
                {"role": "tool", "content": str(observation), "tool_call_id": tool_call.id}
            )
        continue

    messages.append(assistant_message)

    action_match = re.search(r'Action:\s*(\w+)', response_text)
    action_input_match = re.search(r'Action Input:\s*({.*?}|".*?")', response_text, re.DOTALL)

    if action_match and action_input_match:
        tool_name = action_match.group(1)
        params = json.loads(action_input_match.group(1))

        observation = ""
        if tool_name == "get_score_by_name":
            observation = get_score_by_name(params['name'])
            print("人类的回复：Observation: ", observation)
        elif tool_name == "generating_performance_reviews":
            observation = generating_performance_reviews(params['estimation'])
            print("人类的回复: Observation: ", observation)

        messages.append({"role": "user", "content": f"Observation: {observation}"})
