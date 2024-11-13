
def testBusNumInterface():
    import paddle
    # print(paddle.device.cuda.device_count())
    paddle.utils.run_check()

    from Interfaces import BusNumInterface
    # 读取文件
    with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg',
              'rb') as file:
        input = file.read()
    output = BusNumInterface().busNum_detector(input)
    print(output)


def testFunASRInterface():
    from Interfaces import FunASRInterface
    # 调用例子
    # 打开音频文件并以二进制模式读取
    # with open('/home/cike/LJJ/FunASR/test-wav/FinalAudio(1).amr', 'rb') as file:
    with open('/home/cike/HJS/wiseSight/data/FinalAudio.amr', 'rb') as file:
        input = file.read()

    output = FunASRInterface().inferFunction(input)
    print(output)


def testOCRInterface():
    import paddle
    # print(paddle.device.cuda.device_count())
    paddle.utils.run_check()


    from Interfaces import OCRInterface
    # 打开图片文件并以二进制模式读取
    with open('/home/cike/LJJ/paddleOCR/test-images/paper/3.jpg', 'rb') as file:
        input = file.read()
    output = OCRInterface().ocr_direct(input)
    print(output)


def testChatGLMInterface():
    from Interfaces import ChatGLMInterface
    from Interfaces.ChatGLM import toolFunctions
    from Debug import logger
    from time import time

    messages = [
        {
            "role": "system",
            "content": "你是AI智能眼镜，帮助视障群体与老年人的衣食住行。请仔细回答用户的提问。",
        },
        {
            "role": "user",
            # "content":"怎么从大剧院走到广州塔?"
            # "content": "我现在在华南理工大学大学城校区，请问附近的中国银行在哪儿？",
            # "content": "请问对于视障人体出行有什么建议？",
            "content": "这个巴士多少号的？",
            # "content": "番禺的天气如何？",
        },
    ]

    use_stream = False

    input = {
        "functions": toolFunctions,  # 函数定义
        "model": "chatglm3-6b",  # 模型名称
        "messages": messages,  # 会话历史
        "stream": use_stream,  # 是否流式响应
        "max_tokens": 500,  # 最多生成字数
        "temperature": 0.0,  # 温度
        "top_p": 0.8,  # 采样概率
    }
    glm = ChatGLMInterface(device="cuda:7")
    start = time()
    output = glm.inferFunction(input)
    end = time()
    print('time used: ', end - start)
    print(output)
    logger.info(f"Response: {output}")
    if use_stream:
        for i in output:
            print(i)
    else:
        logger.info(f"parsed json: {output.json()}")


def testChatGPTInterface():
    from Interfaces import ChatGPTInterface
    from openai.types.chat import ChatCompletion
    from Interfaces.ChatGLM import toolFunctions
    from Debug import logger

    messages = [
        {
            "role": "system",
            "content": "你是AI智能眼镜，帮助视障群体与老年人的衣食住行。请仔细回答用户的提问。",
        },
        {
            "role": "user",
            # "content":"怎么从大剧院走到广州塔?"
            # "content": "我现在在华南理工大学大学城校区，请问附近的中国银行在哪儿？",
            "content": "请问对于视障人体出行有什么建议？",
            # "content": "红绿灯什么颜色？",
            # "content": "番禺的天气如何？",
        },
    ]

    input = {
        "functions": toolFunctions,  # 函数定义
        # "model": "gpt-3.5-turbo-1106",  # 模型名称
        "messages": messages,  # 会话历史
    }

    output:ChatCompletion = ChatGPTInterface().inferFunction(input)
    print(output)
    # logger.info(f"Response: {output}")
    # messages.append(output.choices[0].message)
    # messages.append({
    #         "tool_call_id": output.choices[0].message.tool_calls[0].id,
    #         "role": "tool",
    #         "name": "get_current_weather",
    #         "content": '''{'province': '广东', 'city': '番禺区', 'adcode': '440113',
    #  'weather': '多云', 'temperature': '13',
    #  'winddirection': '西北', 'windpower': '≤3',
    #  'humidity': '61', 'reporttime': '2024-02-27 16:30:52',
    #  'temperature_float': '13.0', 'humidity_float': '61.0'}'''
    #     })
    #
    # input = {
    #     "functions": toolFunctions,  # 函数定义
    #     # "model": "gpt-3.5-turbo-1106",  # 模型名称
    #     "messages": messages,  # 会话历史
    # }
    # output: ChatCompletion = ChatGPTInterface().inferFunction(input)
    # print(output)

    logger.info(f"parsed json: {output.json()}")


def testLangSAMInterface():
    import io
    from PIL import Image
    from Interfaces import LangSAM_Interface

    with open('/home/cike/hds/langsam/assets/Bollard.jpg', 'rb') as file:
        image = file.read()
    # convert bytes to Image
    image = Image.open(io.BytesIO(image)).convert('RGB')
    # H, W, C

    text_prompt = "bollard.ground.people"
    masks, boxes, phrases, logits = LangSAM_Interface("cuda:7").predict(image, text_prompt)

    print(masks)


def testLapDepthInterface():
    import io
    from time import time
    from PIL import Image
    from Interfaces import LapDepthInterface
    from Interfaces.LapDepthInterface import get_binary_stream_image

    prompt = 'ground . trashcan . people'

    img = Image.open(io.BytesIO(get_binary_stream_image('/home/cike/weiyuancheng/LapDepth-release/assets/povt2.jpg')))

    # calculate a standard time used to predict
    lapdepth = LapDepthInterface("cuda:7")
    start = time()
    guidence = lapdepth.predict(img, prompt)
    end = time()
    print('time used: ', end - start)
    print(guidence)

    # time used: 8.624093770980835 for a 330KB jpg image
    # {}前方{}处有一个障碍物
    # ['正前方近处有一个障碍物', '右前方远处有一个障碍物']


def testDetectionInterface():
    from Interfaces import DetectionInterface
    root_path = "/home/cike/xyq/mmdetction/"
    detect = DetectionInterface("cuda:7")
    with open(root_path + "OIP-C.jpg", 'rb') as f:
        image = f.read()
        result = detect.keyObjectDetector(input=image)  # 识别图片中的重要物体
        print(result)

    result = detect.keyObject_LocationHint(text_object="wallet")
    print(result)

    with open(root_path + "00001.jpg", 'rb') as f:
        image = f.read()
        result = detect.congestionDetector(input=image)
        print(result)

    with open(root_path + "00001.jpg", 'rb') as f:
        image = f.read()
        result = detect.trafficLightDetector(input=image)
        print(result)

    with open(root_path + "bus.jpg", 'rb') as f:
        image = f.read()
        result = detect.busDetector(input=image)
        print(result)


def testAmap_api():
    from Interfaces import Amap_api
    print(Amap_api.transits_statement("广州大剧院", "广州塔"))
    print(Amap_api.walking("广州大剧院", "广州塔"))
    print(Amap_api.get_current_weather("广州市番禺区"))
    print(Amap_api.get_surrounding("广州大剧院", "餐厅"))


if __name__ == "__main__":

    # testFunASRInterface()
    # testBusNumInterface()
    # testOCRInterface()
    testChatGLMInterface()
    # testLangSAMInterface()
    # testLapDepthInterface()
    # testDetectionInterface() // 无法运行在torch2.2上
    # testAmap_api()
    # testChatGPTInterface()



