import io
import json
import time
import traceback
from multiprocessing.shared_memory import ShareableList

from PIL import Image
from openai.types.chat import ChatCompletion
from torch.multiprocessing import Process, Queue, Lock, Value

from Debug import logger
from Interfaces import (
    ChatGLMInterface, DetectionInterface, LapDepthInterface, FunASRInterface, OCRInterface,
    BusNumInterface, ChatGPTInterface
)
from Interfaces.ChatGLM import ChatCompletionResponse, toolFunctions


class ASR_Process(Process):
    def __init__(self, inAudioQueue: Queue, inLanguageQueue: Queue, amapCallQueue: Queue):
        super().__init__()
        self.inAudioQueue = inAudioQueue
        self.inLanguageQueue = inLanguageQueue
        self.amapCallQueue = amapCallQueue
        self.funASR = None

    def run(self):
        self.funASR = FunASRInterface("cuda:0")  # FunASR只能使用cuda0，就像PaddleOCR一样
        logger.info("FunASR initialized successfully.")
        while True:
            audio = self.inAudioQueue.get()

            try:
                text = self.funASR.inferFunction(audio)
            except Exception as e:
                logger.error(f"ASR_Process error: {e}")
                continue

            logger.info(f"ASR: {text}")

            if len(text.strip()) < 2:
                continue
            elif "停止导航" in text or "关闭导航" in text or "取消导航" in text or "结束导航" in text:
                instruction = {
                    "function_call": {
                        "name": "stop_navigate",
                        "arguments": None,
                    },
                    "chat_messages": []
                }
                # 停止导航
                self.amapCallQueue.put(instruction)
                continue

            self.inLanguageQueue.put([
                {
                    "role": "system",
                    "content": "你是AI智能眼镜，帮助视障群体与老年人的衣食住行。请根据需要调用所给的工具函数，仔细回答用户的提问。",
                },
                {
                    "role": "user",
                    "content": text,
                }
            ])


class Chat_Process(Process):
    def __init__(self, inLanguageQueue: Queue, outTextQueue: Queue,
                 amapCallQueue: Queue, detectionCallQueue: Queue, ocrCallQueue: Queue):
        super().__init__()
        self.inLanguageQueue, self.outTextQueue, self.amapCallQueue, self.detectionCallQueue, self.ocrCallQueue = (
            inLanguageQueue, outTextQueue, amapCallQueue, detectionCallQueue, ocrCallQueue
        )
        self.chatglm = None
        self.chatgpt = None

    def make_input(self, messages):
        input_dict = {
            "functions": toolFunctions,  # 函数定义
            "model": "chatglm3-6b",  # 模型名称
            "messages": messages,  # 会话历史
            "stream": False,  # 是否流式响应
            "max_tokens": 128,  # 最多生成字数
            "temperature": 0.0,  # 温度
            "top_p": 0.8,  # 采样概率
        }
        return input_dict

    def run(self):

        WHICH_TO_USE = 0
        match WHICH_TO_USE:
            case 0:
                self.chatgpt = ChatGPTInterface()
            case 1:
                self.chatglm = ChatGLMInterface("cuda:2")

        logger.info("ChatGLM initialized successfully.")
        while True:
            messages = self.inLanguageQueue.get()
            print(messages)
            try:
                match WHICH_TO_USE:
                    case 0:
                        self.response_with_gpt(messages)
                    case 1:
                        self.response_with_glm(messages)
            except KeyboardInterrupt:
                exit(WHICH_TO_USE)
            except Exception as e:
                print(traceback.format_exc())
                logger.error(f"Chat_Process error: {e}")
                continue

    def response_with_gpt(self, messages):
        response: ChatCompletion = self.chatgpt.inferFunction(self.make_input(messages))
        '''两个示例
        ChatCompletion(id='chatcmpl-8teu6dCm773ckanxeFoASPt6wiEz7', 
            choices=[Choice(finish_reason='stop', index=0,
                        message=ChatCompletionMessage(
                            content='嗨，当然可以讲一个故事给你听。这是一个关于勇敢的小猫咪的故事。\n\n从前，有一只叫做小花的小猫咪，它非常非常勇敢。有一天，小花听说森林里的树林里有一个神奇的宝藏，但是要到达宝藏的地方需要穿越一片茂密的树林和一个瀑布。小花决定踏上这次刺激的冒险之旅！\n\n小花开始了她的旅程，她穿过了茂密的树林，见到了不少小伙伴们。有一只叫做小松鼠的小伙伴告诉小花，在这片树林内，生活着许多危险的动物，而要抵达宝藏之地，她还需要很大的勇气。\n\n小花并没有感到害怕，她继续向前走去。当她来到了瀑布前，她发现瀑布非常大，水势非常猛烈，看起来无法横渡。小花决定寻找出路，她跳上一块靠近瀑布的岩石，试图找到可以穿越瀑布的方式。\n\n终于，小花发现了一条隐藏的岩洞，她小心翼翼地钻进去，然后绕过了瀑布，来到宝藏的地方。在那里，她发现了一颗闪闪发光的宝石，宝石上写着：“勇气和毅力的奖赏”。\n\n小花拿起宝石，回头看了看她所经历的一切，她觉得非常欣慰。她明白，勇气和毅力可以克服一切困难，也能收获最珍贵的宝藏。\n\n小花将宝石带回了家，从此以后，她成为了所有小猫咪们心目中的英雄。这就是小花勇敢而充满冒险精神的故事，希望你喜欢！',
                            role='assistant',
                            function_call=None,
                            tool_calls=None), delta=None)],
                       created=1708275966, model='gpt-3.5-turbo-1106', object='chat.completion',
                       system_fingerprint=None,
                       usage=CompletionUsage(completion_tokens=658, prompt_tokens=638, total_tokens=1296))
        ChatCompletion(id='chatcmpl-8tf0btqBhdNNBP6E1KBMa0cz9LBCs', 
            choices=[Choice(finish_reason='tool_calls', index=0,
                            message=ChatCompletionMessage(
                                content=None, role='assistant',
                                function_call=None, tool_calls=[
                                    ChatCompletionMessageToolCall(
                                        id='call_KXipV4yM1ZLyZ8HDtca9uwrU',
                                        function=Function(
                                            arguments='{"origin":"大剧院","destination":"广州塔"}',
                                            name='walking_from_org_to_dst'),
                                        type='function')]),
                            delta=None)], created=1708276369,
                       model='gpt-3.5-turbo-1106', object='chat.completion', system_fingerprint=None,
                       usage=CompletionUsage(completion_tokens=28, prompt_tokens=648, total_tokens=676))
        '''
        self.deal_with_response(response, messages, "chatgpt")

    def response_with_glm(self, messages):
        response: ChatCompletionResponse = self.chatglm.inferFunction(self.make_input(messages))
        '''一个示例
        model = 'chatglm3-6b'
        object = 'chat.completion'
        choices = [ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(
                role='assistant',
                content="path_from_org_to_dst\n ```python\ntool_call(origin='大剧院', destination='广州塔', mode='walking')\n```",
                name=None,
                function_call=FunctionCallResponse(
                    name='path_from_org_to_dst',
                    arguments='{"origin": "大剧院", "destination": "广州塔", "mode": "walking"}'
                )
            ),
            finish_reason='function_call')]
        created = 1703779877
        usage = UsageInfo(prompt_tokens=688, total_tokens=725, completion_tokens=37)
        '''
        self.deal_with_response(response, messages, "chatglm")

    def deal_with_response(self, response, messages, chat_model):
        logger.info(response)
        choice = response.model_dump().get("choices", [{}])[0]
        msg = choice.get("message", {})
        messages.append(msg)

        if self.isFunctionCall(choice.get("finish_reason", None)):
            self.addCallQueue(msg, messages, chat_model)
        else:
            self.outTextQueue.put(messages)

    def isFunctionCall(self, finish_reason):
        if finish_reason is None:
            return False
        return finish_reason == 'function_call' or finish_reason == 'tool_calls'

    def addCallQueue(self, msg, messages, chat_model):
        if chat_model == "chatgpt":
            function_name = msg["tool_calls"][0]["function"]["name"].strip()
            function_arg = msg["tool_calls"][0]["function"]["arguments"]
            tool_call_id = msg["tool_calls"][0]["id"]
        else:
            function_name = msg["function_call"]["name"].strip()
            function_arg = msg["function_call"]["arguments"]
            tool_call_id = None
        instruction = {
            "function_call": {
                "id": tool_call_id,
                "name": function_name,
                "arguments": function_arg,
            },
            "chat_messages": messages
        }
        logger.info(f"function_call: ${function_name}")
        match function_name:
            case "bus_num_detector" | "ocr_direct":
                self.ocrCallQueue.put(instruction)
            case "congestion_detector" | "traffic_light_detection" | "key_object_location_hint":
                self.detectionCallQueue.put(instruction)
            case "get_current_weather" | "get_surrounding" | "transits_from_org_to_dst" | "walking_from_org_to_dst":
                self.amapCallQueue.put(instruction)
            case _:
                logger.error(f"ChatGLM_Process Unknown function name: {function_name}")
                return
                # raise ValueError(function_name)


class Image_Process(Process):
    def __init__(self, imageContainer: ShareableList, imageReadingLock: Lock,
                 imageReaderCount: Value, imageReaderCountLock: Lock,
                 imageWritingLock: Lock):
        super().__init__()

        self.imageContainer, self.imageReadingLock, self.imageReaderCount, self.imageReaderCountLock, self.imageWritingLock = (
            imageContainer, imageReadingLock, imageReaderCount, imageReaderCountLock, imageWritingLock
        )

    def run(self):
        pass

    def detect(self):
        pass

    def _beforeReading(self):
        self.imageWritingLock.acquire()
        self.imageReaderCountLock.acquire()
        if self.imageReaderCount.value == 0:
            self.imageReadingLock.acquire()
        self.imageReaderCount.value += 1
        self.imageReaderCountLock.release()
        self.imageWritingLock.release()

    def _afterReading(self):
        self.imageReaderCountLock.acquire()
        self.imageReaderCount.value -= 1
        if self.imageReaderCount.value == 0:
            self.imageReadingLock.release()
        self.imageReaderCountLock.release()

    def readImage(self):
        self._beforeReading()
        image = self.imageContainer[0]
        self._afterReading()
        return image


class Detection_Process(Image_Process):
    def __init__(self, imageContainer, imageReadingLock: Lock,
                 imageReaderCount, imageReaderCountLock: Lock,
                 imageWritingLock: Lock,
                 inLanguageQueue: Queue, outTextQueue: Queue, detectionCallQueue: Queue):
        super().__init__(imageContainer, imageReadingLock, imageReaderCount, imageReaderCountLock,
                         imageWritingLock)

        self.inLanguageQueue = inLanguageQueue
        self.outTextQueue = outTextQueue
        self.detectionCallQueue = detectionCallQueue

        self.objectDetection = None

    def run(self):
        self.objectDetection = DetectionInterface("cuda:0")
        logger.info("Detection initialized successfully.")
        while True:

            if self.detectionCallQueue.empty():
                instruction = None
            else:
                instruction = self.detectionCallQueue.get()

            image = self.readImage()
            if image is None:
                time.sleep(1)
                continue

            try:
                self.detect(instruction, image)
            except Exception as e:
                logger.error(f"Detection_Process error: ${e}")

    def detect(self, instruction, image):
        if instruction is None:
            found_obj = self.objectDetection.keyObjectDetector(image)
            if len(found_obj) > 0:
                print(found_obj)
            return

        function_name = instruction["function_call"]["name"].strip()
        function_arg = instruction["function_call"]["arguments"]
        match function_name:
            case "key_object_location_hint":
                thing = json.loads(function_arg)["thing"]

                # 转换中英文
                match thing:
                    case "钥匙":
                        text_object = "key"
                    case "钱包":
                        text_object = "wallet"
                    case "手机":
                        text_object = "cellular_telephone"
                    case "遥控器":
                        text_object = "remote"
                    case _:
                        text_object = thing

                text = self.objectDetection.keyObject_LocationHint(text_object=text_object)

                message = make_message4func(function_name, text, instruction["function_call"].get("id", None))
                instruction["chat_messages"].append(message)
                self.inLanguageQueue.put(instruction["chat_messages"])
                return

            case "traffic_light_detection":
                text = self.objectDetection.trafficLightDetector(image)
            case "congestion_detector":
                text = self.objectDetection.congestionDetector(image)
            case 4:
                # 暂时先不管
                text = self.objectDetection.busDetector(image)
            case _:
                logger.error(f"Detection_Process Unknown function name: {function_name}")
                return

        message = make_message4func(function_name, text, instruction["function_call"].get("id", None))
        instruction["chat_messages"].append(message)
        self.outTextQueue.put(instruction["chat_messages"])

        logger.info(f"Detection: {text}")


class Depth_Process(Image_Process):
    def __init__(self, imageContainer, imageReadingLock: Lock,
                 imageReaderCount, imageReaderCountLock: Lock,
                 imageWritingLock: Lock,
                 outTextQueue: Queue, prompt: str = 'ground . trashcan . people'):
        super().__init__(imageContainer, imageReadingLock, imageReaderCount, imageReaderCountLock,
                         imageWritingLock)

        self.outTextQueue = outTextQueue
        self.prompt = prompt
        self.depthEstimation = None
        self.last_result = None

    def run(self):
        self.depthEstimation = LapDepthInterface("cuda:1")
        logger.info("DepthEstimation initialized successfully.")
        while True:
            imageBytes = self.readImage()
            if imageBytes is None:
                self.last_result = None
                time.sleep(1)
                continue

            try:
                image = Image.open(io.BytesIO(imageBytes)).convert('RGB')
                self.detect(image, self.prompt)
            except Exception as e:
                logger.error(f"Depth_Process error {e}")

    def detect(self, image, prompt):
        text = self.depthEstimation.predict(image, prompt)
        if len(text) > 0:
            if text == self.last_result:
                return
            self.last_result = text
            message = make_message4func("depth_estimation", text)
            self.outTextQueue.put([message])
            logger.info(f"Depth Estimation: {text}")


class OCR_Process(Image_Process):
    def __init__(self, imageContainer, imageReadingLock: Lock,
                 imageReaderCount, imageReaderCountLock: Lock,
                 imageWritingLock: Lock,
                 inLanguageQueue: Queue, ocrCallQueue: Queue):
        super().__init__(imageContainer, imageReadingLock, imageReaderCount, imageReaderCountLock,
                         imageWritingLock)

        self.inLanguageQueue = inLanguageQueue
        self.ocrCallQueue = ocrCallQueue
        self.ocr = None
        self.busNum = None

    def run(self):
        self.ocr = OCRInterface()  # PaddleOCR只能使用cuda0，就像FunASRInterface一样
        self.busNum = BusNumInterface("cuda:0")
        logger.info("OCR initialized successfully.")

        while True:
            instruction = self.ocrCallQueue.get()

            image = self.readImage()
            if image is None:
                time.sleep(1)
                continue
            try:
                self.detect(image, instruction)
            except Exception as e:
                logger.error(f"OCR_Process error: ${e}")

    def detect(self, image, instruction):
        function_name = instruction["function_call"]["name"].strip()
        match function_name:
            case "ocr_direct":
                text = self.ocr.ocr_direct(image)
            case "bus_num_detector":
                text = self.busNum.busNum_detector(image)
            case _:
                logger.error(f"OCR_Process Unknown function name: {function_name}")
                return
                # raise ValueError(instruction)

        message = make_message4func(function_name, text, instruction["function_call"].get("id", None))

        instruction["chat_messages"].append(message)
        self.inLanguageQueue.put(instruction["chat_messages"])

        logger.info(f"OCR: {text}")


def make_message4func(function_name, text, tool_call_id=None):
    if tool_call_id is not None:
        message = {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": function_name,
            "content": str(text),
        }
    else:
        message = {
            "role": "function",
            "name": function_name,
            "content": str(text),
        }
    return message
