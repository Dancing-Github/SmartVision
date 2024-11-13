import asyncio
import time


def testAmap():
    # import os
    from Cores.Threading import Amap_Thread
    from torch.multiprocessing import Queue
    import torch.multiprocessing as mp
    mp.set_start_method('spawn', force=True)

    inLanguageQueue, outTextQueue, amapCallQueue = Queue(), Queue(), Queue()

    amap_thread = Amap_Thread(inLanguageQueue, outTextQueue,
                              amapCallQueue)
    amap_thread.start()

    amapCallQueue.put({
        "function_call": {
            "name": "walking",
            "arguments": '{"origin": "华南理工大学大学城校区", "destination": "中山大学大学城校区"}',
        },
        "chat_messages": [
            {
                "role": "user",
                "content": "我现在在华南理工大学大学城校区，请问如何步行至中山大学大学城校区",
            },
            {
                "role": "assistant",
                "content": "walking_from_org_to_dst\n ```python\ntool_call(origin=origin, destination=destination)\n```",
                "function_call": {
                    "name": "walking_from_org_to_dst",
                    "arguments": '{"origin": "华南理工大学大学城校区", "destination": "中山大学大学城校区"}',
                },
            },
        ]

    })

    amapCallQueue.put({
        'function_call': {
            'id': 'call_dRBzopFLvP8TkkTbKlNZCyyk', 'name': 'get_current_weather',
            'arguments': '{"location":"广州"}'
        },

        'chat_messages': [
            {'role': 'user', 'content': '广州的天气如何？'},
            {
                'content': None, 'role': 'assistant', 'function_call': None,
                'tool_calls': [
                    {
                        'id': 'call_dRBzopFLvP8TkkTbKlNZCyyk',
                        'function': {
                            'arguments': '{"location":"广州"}',
                            'name': 'get_current_weather'
                        },
                        'type': 'function'
                    }
                ]
            }
        ]
    })
    # 异步返回
    # print(inLanguageQueue.get())

    amapCallQueue.put({
        "function_call": {
            "name": "get_surrounding",
            "arguments": '{"address": "华南理工大学大学城校区", "keywords": "电影院"}',
        },
        "chat_messages": [
            {
                "role": "user",
                # "content": "我现在在华南理工大学大学城校区，请问附近的中国银行在哪儿？",
                "content": "请问华南理工大学大学城校区最近的电影院在哪里？",
            },
            {
                "role": "assistant",
                "content": "get_surrounding\n ```python\ntool_call(address=address, keywords=keywords)\n```",
                "function_call": {
                    "name": "get_surrounding",
                    "arguments": '{"address": "华南理工大学大学城校区", "keywords": "电影院"}',
                },
            },
        ]

    })

    # print(inLanguageQueue.get())  # 获取输入GLM的队列
    print(outTextQueue.get())  # 获取直接返回android的队列

    time.sleep(20)

    amapCallQueue.put({
        "function_call": {
            "name": "stop_navigate",
            "arguments": None,
        },
        "chat_messages": []
    })
    print(outTextQueue.get())

    amap_thread.join()


if __name__ == '__main__':
    testAmap()
