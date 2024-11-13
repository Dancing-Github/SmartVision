import time


def testMultiProcessing():
    from multiprocessing.shared_memory import ShareableList
    with open("/home/cike/xyq/mmdetction/bus.jpg", 'rb') as f:
        image = f.read()
    imageContainer = ShareableList([b' ' * 1024 * 1024 * 9])  # 9MB
    imageContainer[0] = None
    imageContainer[0] = image
    print(imageContainer[0] == image)
    # imageContainer.shm.close()
    imageContainer.shm.unlink()


def testASR_Process():
    import os
    from Cores.Processing import ASR_Process
    from torch.multiprocessing import Queue
    import torch.multiprocessing as mp
    os.environ['CUDA_VISIBLE_DEVICES'] = '2'
    mp.set_start_method('spawn', force=True)

    inLanguageQueue, inAudioQueue, amapCallQueue = Queue(), Queue(), Queue()

    asr_process = ASR_Process(inAudioQueue, inLanguageQueue, amapCallQueue)
    asr_process.start()

    with open('/home/cike/HJS/wiseSight/data/FinalAudio.amr', 'rb') as file:
        input = file.read()

    inAudioQueue.put(input)
    print(inLanguageQueue.get())

    with open('/home/cike/HJS/wiseSight/data/stopnavi.amr', 'rb') as file:
        input = file.read()

    inAudioQueue.put(input)
    print(amapCallQueue.get())
    asr_process.join()


def testDepth_Process():
    # import os
    from multiprocessing.shared_memory import ShareableList
    from Cores.Processing import Depth_Process
    from torch.multiprocessing import Queue, Lock, Value
    import torch.multiprocessing as mp
    mp.set_start_method('spawn', force=True)
    # os.environ['CUDA_VISIBLE_DEVICES'] = '2'

    outTextQueue = Queue()

    imageReadingLock, imageReaderCountLock, imageWritingLock, imageWriterCountLock = (
        Lock(), Lock(), Lock(), Lock())

    imageReaderCount, imageWriterCount = Value('i', 0), Value('i', 0)
    imageContainer = ShareableList([b' ' * 1024 * 1024 * 9])  # 9MB image max size
    imageContainer[0] = None

    depth_process = Depth_Process(imageContainer, imageReadingLock,
                                  imageReaderCount, imageReaderCountLock,
                                  imageWritingLock,
                                  outTextQueue)
    depth_process.start()

    with open('/home/cike/weiyuancheng/LapDepth-release/assets/povt2.jpg', 'rb') as file:
        input = file.read()
    #########################################
    imageWriterCountLock.acquire()
    if imageWriterCount.value == 0:
        imageWritingLock.acquire()
    imageWriterCount.value += 1
    imageWriterCountLock.release()
    imageReadingLock.acquire()
    imageContainer[0] = input  # set img
    imageReadingLock.release()
    imageWriterCountLock.acquire()
    imageWriterCount.value -= 1
    if imageWriterCount.value == 0:
        imageWritingLock.release()
    imageWriterCountLock.release()
    ########################################
    print(outTextQueue.get())

    depth_process.join()


def testOCR_Process():
    # import os
    from multiprocessing.shared_memory import ShareableList
    from Cores.Processing import OCR_Process
    from torch.multiprocessing import Queue, Lock, Value
    import torch.multiprocessing as mp
    mp.set_start_method('spawn', force=True)
    # os.environ['CUDA_VISIBLE_DEVICES'] = '2'

    inLanguageQueue, ocrCallQueue = Queue(), Queue()

    imageReadingLock, imageReaderCountLock, imageWritingLock, imageWriterCountLock = (
        Lock(), Lock(), Lock(), Lock())

    imageReaderCount, imageWriterCount = Value('i', 0), Value('i', 0)
    imageContainer = ShareableList([b' ' * 1024 * 1024 * 9])  # 9MB image max size
    imageContainer[0] = None

    ocr_process = OCR_Process(imageContainer, imageReadingLock,
                              imageReaderCount, imageReaderCountLock,
                              imageWritingLock,
                              inLanguageQueue, ocrCallQueue)
    ocr_process.start()

    ocrCallQueue.put({
        "function_call": {
            "name": "bus_num_detector",
            "arguments": '{}',
        },
        "chat_messages": [
            {
                "role": "user",
                "content": "那辆公交车牌号是多少？"
            },

            {
                "role": "assistant",
                "content": "bus_num_detector\n ```python\ntool_call()\n```",
                "function_call": {
                    "name": "bus_num_detector",
                    "arguments": '{}',
                },
            }
        ]
    })
    with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg',
              'rb') as file:
        input = file.read()
    #########################################
    imageWriterCountLock.acquire()
    if imageWriterCount.value == 0:
        imageWritingLock.acquire()
    imageWriterCount.value += 1
    imageWriterCountLock.release()
    imageReadingLock.acquire()
    imageContainer[0] = input  # set img
    imageReadingLock.release()
    imageWriterCountLock.acquire()
    imageWriterCount.value -= 1
    if imageWriterCount.value == 0:
        imageWritingLock.release()
    imageWriterCountLock.release()
    ########################################
    print(inLanguageQueue.get())

    ocrCallQueue.put({
        "function_call": {
            "name": "ocr_direct",
            "arguments": '{}',
        },
        "chat_messages": [
            {
                "role": "user",
                "content": "这上面写了什么？",
            },

            {
                "role": "assistant",
                "content": "ocr_direct\n ```python\ntool_call()\n```",
                "function_call": {
                    "name": "ocr_direct",
                    "arguments": '{}',
                },
            }
        ]

    })
    with open('/home/cike/LJJ/paddleOCR/test-images/paper/3.jpg', 'rb') as file:
        input = file.read()
    #########################################
    imageWriterCountLock.acquire()
    if imageWriterCount.value == 0:
        imageWritingLock.acquire()
    imageWriterCount.value += 1
    imageWriterCountLock.release()
    imageReadingLock.acquire()
    imageContainer[0] = input  # set img
    imageReadingLock.release()
    imageWriterCountLock.acquire()
    imageWriterCount.value -= 1
    if imageWriterCount.value == 0:
        imageWritingLock.release()
    imageWriterCountLock.release()
    ########################################
    print(inLanguageQueue.get())

    ocr_process.join()


def testDetection_Process():
    # import os
    # os.environ['CUDA_VISIBLE_DEVICES'] = '2'
    from Cores.Processing import Detection_Process
    from multiprocessing.shared_memory import ShareableList
    from torch.multiprocessing import Queue, Lock, Value
    import torch.multiprocessing as mp
    mp.set_start_method('spawn', force=True)

    (inLanguageQueue, outTextQueue,
     amapCallQueue, detectionCallQueue, ocrCallQueue) = (
        Queue(), Queue(), Queue(), Queue(), Queue() )

    imageReadingLock, imageReaderCountLock, imageWritingLock, imageWriterCountLock = (
        Lock(), Lock(), Lock(), Lock())

    imageReaderCount, imageWriterCount = Value('i', 0), Value('i', 0)

    imageContainer = ShareableList([b' ' * 1024 * 1024 * 9])  # 9MB image max size
    imageContainer[0] = None
    detection_process = Detection_Process(imageContainer, imageReadingLock,
                                          imageReaderCount, imageReaderCountLock,
                                          imageWritingLock,
                                          inLanguageQueue, outTextQueue, detectionCallQueue)
    detection_process.start()

    root_path = "/home/cike/xyq/mmdetction/"
    test_imgs = ["OIP-C.jpg", "wallet.jpg", "00001.jpg", "00001.jpg"]
    for idx in range(len(test_imgs)):
        with open(root_path + test_imgs[idx], 'rb') as f:
            inputImg = f.read()

        #########################################
        imageWriterCountLock.acquire()
        if imageWriterCount.value == 0:
            imageWritingLock.acquire()
        imageWriterCount.value += 1
        imageWriterCountLock.release()
        imageReadingLock.acquire()
        imageContainer[0] = inputImg  # set img
        imageReadingLock.release()
        imageWriterCountLock.acquire()
        imageWriterCount.value -= 1
        if imageWriterCount.value == 0:
            imageWritingLock.release()
        imageWriterCountLock.release()
        ########################################
        match idx:
            case 0:
                time.sleep(1)  # 等待检测key object与保存信息
            case 1:
                detectionCallQueue.put({
                    "function_call": {
                        "name": "key_object_location_hint",
                        "arguments": '{"thing": "key"}',
                    },
                    "chat_messages": [
                        {
                            "role": "user",
                            "content": "钥匙哪去了",
                        },

                        {
                            "role": "assistant",
                            "content": "key_object_location_hint\n ```python\ntool_call(thing='key')\n```",
                            "function_call": {
                                "name": "key_object_location_hint",
                                "arguments": '{"thing": "key"}',
                            },
                        },
                    ]

                })
                print(inLanguageQueue.get())
            case 2:
                detectionCallQueue.put({
                    "function_call": {
                        "name": "congestion_detector",
                        "arguments": '{}',
                    },
                    "chat_messages": [
                        {
                            "role": "user",
                            "content": "路上车多吗？",
                        },
                        {
                            "role": "assistant",
                            "content": "congestion_detector\n ```python\ntool_call()\n```",
                            "function_call": {
                                "name": "congestion_detector",
                                "arguments": '{}',
                            },
                        }
                    ]

                })
                print(outTextQueue.get())
            case 3:
                detectionCallQueue.put({
                    "function_call": {
                        "name": "traffic_light_detection",
                        "arguments": '{}',
                    },
                    "chat_messages": [
                        {
                            "role": "user",
                            "content": "红绿灯现在是什么颜色",
                        },

                        {
                            "role": "assistant",
                            "content": "traffic_light_detection\n ```python\ntool_call()\n```",
                            "function_call": {
                                "name": "traffic_light_detection",
                                "arguments": '{}',
                            }
                        }
                    ]

                })
                print(outTextQueue.get())
            case 4:
                pass  # 暂时先不管
                # detectionCallQueue.put("busDetector")

    detection_process.join()


def testChat_Process():
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = "5,6"
    from Cores.Processing import Chat_Process
    from torch.multiprocessing import Queue
    import torch.multiprocessing as mp
    mp.set_start_method('spawn', force=True)

    (inLanguageQueue, outTextQueue,
     amapCallQueue, detectionCallQueue, ocrCallQueue) = (
        Queue(), Queue(), Queue(), Queue(), Queue())

    '''
    inLanguageQueue：存放语音识别结果、函数回调的信息等需要LLM处理的文本，将会输入到ChatGLM
    outTextQueue：存放完成处理后的文本，将会输出到安卓设备，使用tts播放
    amapCallQueue：存放ChatGLM输出的高德函数调用信息，将会输入到Amap做函数调用
    detectionCallQueue：存放ChatGLM输出的物体检测的调用指令，将会输入到mmDetection做函数调用
    ocrCallQueue：存放ChatGLM输出的OCR的调用指令，将会输入到OCR做函数调用
    '''

    glm_process = Chat_Process(inLanguageQueue, outTextQueue,
                               amapCallQueue, detectionCallQueue, ocrCallQueue)
    glm_process.start()

    inLanguageQueue.put([{
        "role": "user",
        "content": "广州的天气如何？",
    }])
    print(amapCallQueue.get())  # 希望ChatGLM能够调用高德天气接口, 检查格式是否正确

    # inLanguageQueue.put([{
    #     "role": "user",
    #     "content": "讲一段故事吧",
    # }])
    # print(outTextQueue.get())  # 这个队列的内容直接发送到安卓端，安卓端使用tts播放

    glm_process.join()


if __name__ == '__main__':
    # testMultiProcessing()
    # testASR_Process()
    # testDepth_Process()
    # testOCR_Process()
    # testDetection_Process()
    testChat_Process()
