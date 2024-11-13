import json
from openai import OpenAI
import threading

from openai.types.chat import ChatCompletion


#
# def run_conversation():
#     # Step 1: send the conversation and available functions to the model
#     messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
#     tools = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_current_weather",
#                 "description": "Get the current weather in a given location",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "location": {
#                             "type": "string",
#                             "description": "The city and state, e.g. San Francisco, CA",
#                         },
#                         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                     },
#                     "required": ["location"],
#                 },
#             },
#         }
#     ]
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo-1106",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto",  # auto is default, but we'll be explicit
#     )
#     response_message = response.choices[0].message
#     tool_calls = response_message.tool_calls
#     # Step 2: check if the model wanted to call a function
#     if tool_calls:
#         # Step 3: call the function
#         # Note: the JSON response may not always be valid; be sure to handle errors
#         available_functions = {
#             "get_current_weather": get_current_weather,
#         }  # only one function in this example, but you can have multiple
#         messages.append(response_message)  # extend conversation with assistant's reply
#         # Step 4: send the info for each function call and function response to the model
#         for tool_call in tool_calls:
#             function_name = tool_call.function.name
#             function_to_call = available_functions[function_name]
#             function_args = json.loads(tool_call.function.arguments)
#             function_response = function_to_call(
#                 location=function_args.get("location"),
#                 unit=function_args.get("unit"),
#             )
#             messages.append(
#                 {
#                     "tool_call_id": tool_call.id,
#                     "role": "tool",
#                     "name": function_name,
#                     "content": function_response,
#                 }
#             )  # extend conversation with function response
#         second_response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#         )  # get a new response from the model where it can see the function response
#         return second_response
#

class ChatGPTInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ChatGPTInterface, "_instance"):
            with ChatGPTInterface._instance_lock:
                if not hasattr(ChatGPTInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    ChatGPTInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return ChatGPTInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self):
        # aiproxy API Key
        api_key = "sk-ndBwM52IG0kKK64KSqMha7VeKR9rx6u0oaozHCngkObODxsr"

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.aiproxy.io/v1"
        )

    def inferFunction(self, input)->ChatCompletion:
        # input.update({
        #     "functions": functions,  # 函数定义
        #     "model": model,  # 模型名称
        #     "messages": messages,  # 会话历史
        #     "stream": use_stream,  # 是否流式响应
        #     "max_tokens": 100,  # 最多生成字数
        #     "temperature": 0.0,  # 温度
        #     "top_p": 0.8,  # 采样概率
        # })
        tools = [{
            "type": "function",
            "function": f
        } for f in input["functions"]]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=input["messages"],
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        # print(response)
        # response.choices[0].message.content="广州番禺目前的天气是多云，气温为13摄氏度，湿度为61%，体感较凉，出行注意保暖哦！"
        return response
