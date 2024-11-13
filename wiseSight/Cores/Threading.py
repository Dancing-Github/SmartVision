import traceback
import json
import time
from threading import Thread

from torch.multiprocessing import Queue

from Cores.Processing import make_message4func
from Debug import logger
from Interfaces import transits_statement, walking, get_current_weather, get_surrounding, get_location


class Amap_Thread(Thread):
    def __init__(self, inLanguageQueue: Queue, outTextQueue: Queue, amapCallQueue: Queue):
        super().__init__()
        self.inLanguageQueue = inLanguageQueue
        self.outTextQueue = outTextQueue
        self.amapCallQueue = amapCallQueue
        # self.navigateThread = None
        self.navigating = False

    def run(self):
        while True:
            instruction = self.amapCallQueue.get()
            try:
                self.function_call(instruction)
            except Exception as e:
                print(traceback.format_exc())
                logger.error(
                    f"Amap_Thread call {instruction['function_call']['name']}({instruction['function_call']['arguments']}) failed: {e}")

    def function_call(self, instruction):
        function_name = instruction["function_call"]["name"].strip()
        function_arg = instruction["function_call"]["arguments"]

        match function_name:
            case "get_current_weather":
                location = json.loads(function_arg)["location"]
                text = get_current_weather(location)
            case "get_surrounding":
                location = json.loads(function_arg)["address"]
                keywords = json.loads(function_arg)["keywords"]
                text = get_surrounding(location, keywords)
            case "transits_from_org_to_dst":
                try:
                    origin = json.loads(function_arg)["origin"]
                    destination = json.loads(function_arg)["destination"]
                    text = transits_statement(origin, destination)
                except Exception as e:
                    print(traceback.format_exc())
                    text = "定位模糊，请说出详细地址"
            case "stop_navigate":
                self.stop_navigate()
                text = "导航结束"
            case "walking_from_org_to_dst":
                try:
                    origin = json.loads(function_arg)["origin"]
                    destination = json.loads(function_arg)["destination"]
                    # routine = walking(origin, destination)
                    # if self.navigating is False:
                    #     logger.info("创建导航")
                    #     self.navigating = True
                    #     Thread(target=self.navigate, args=(routine,)).start()
                    # return
                    # {'location': '113.783993,23.047200', 'citycode': '0769', 'adcode': '441900'}
                    text = get_location(destination)['location']
                except Exception as e:
                    print(traceback.format_exc())
                    text = f"获取位置失败"
            case _:
                raise ValueError(instruction)

        message = make_message4func(function_name, text, instruction["function_call"].get("id", None))
        instruction["chat_messages"].append(message)

        # self.inLanguageQueue.put(instruction["chat_messages"])  # 传给chatglm
        self.outTextQueue.put(instruction["chat_messages"])  # 传给android端

        logger.info(f"Function call {function_name}({function_arg}) returned {text}")

    def stop_navigate(self):
        self.navigating = False
        logger.info("导航结束")

    def navigate(self, routine):

        logger.info("导航开始")
        # outTextQueue 直接输出到 android 端
        self.outTextQueue.put([{
            "role": "function", "name": "navigate",
            "content": f"导航开始,全程{routine['total_distance']}米,预计用时{int(routine['total_duration']) / 60}分钟"}])

        # self.navigateTask = True
        '''
        {'total_distance': '2941', 'total_duration': '2353', 'steps': [
            {'instruction': '向东南步行48米右转', 'orientation': '东南', 'road': [], 'distance': '48', 'duration': '38',
             'polyline': '113.322569,23.114996;113.322765,23.114744;113.322765,23.114744;113.322852,23.114648',
             'action': '右转', 'assistant_action': [], 'walk_type': '0'},
            {'instruction': '沿滨江东路向东步行875米右转', 'orientation': '东', 'road': '滨江东路', 'distance': '875',
             'duration': '700',
             'polyline': '113.315755,23.105629;113.315825,23.105694;113.315898,23.105734;113.31612,23.105812;113.31628,23.10589;113.316372,23.105964;113.316623,23.106241;113.316701,23.106289;113.316814,23.106345;113.317791,23.106688;113.318103,23.106788;113.31829,23.106832;113.318542,23.106858;113.318746,23.106866;113.318845,23.106866;113.318845,23.106866;113.319119,23.106862;113.31921,23.106845;113.319358,23.106784;113.319449,23.106749;113.319449,23.106749;113.31957,23.106749;113.320569,23.10684;113.320569,23.10684;113.321363,23.106927;113.321363,23.106927;113.322088,23.107031;113.322248,23.107057;113.3225,23.107148;113.3225,23.107148;113.322986,23.107179;113.322986,23.107179;113.323529,23.107201;113.323529,23.107201;113.323585,23.107205;113.323728,23.107205;113.323728,23.107205;113.323911,23.107196',
             'action': '右转', 'assistant_action': [], 'walk_type': '0'},
            {'instruction': '步行29米到达目的地', 'orientation': [], 'road': [], 'distance': '29', 'duration': '23',
             'polyline': '113.323911,23.107192;113.323893,23.106927', 'action': [], 'assistant_action': '到达目的地',
             'walk_type': '0'}
        ]}
        '''

        for step in routine["steps"]:

            text = step["instruction"]  # 播报内容
            wait = int(step["duration"])  # 等待时间 s
            logger.info(f"导航播报：{text}, 等待{wait}秒")

            self.outTextQueue.put([{"role": "function", "name": "navigate", "content": text}])
            # time.sleep(1)
            while wait:
                if self.navigating is False:
                    return
                wait -= 1
                time.sleep(1)


# a counter_image thread work as timer , with a function to reset timer
class Timer_Thread(Thread):
    def __init__(self, setImageFunction, setLocationFunction):
        super().__init__()
        self.counter_image = 0
        self.counter_location = 0
        self.setImageFunction = setImageFunction
        self.setLocationFunction = setLocationFunction

    def run(self):
        while True:
            self.counter_image += 1
            self.counter_location += 1
            time.sleep(1)

            if self.counter_image == 10:
                self.counter_image = 0
                self.setImageFunction(None)

            if self.counter_location == 30:
                self.counter_location = 0
                self.setLocationFunction(None)

    def resetTimerImage(self):
        self.counter_image = 0

    def resetTimerLocation(self):
        self.counter_location = 0
