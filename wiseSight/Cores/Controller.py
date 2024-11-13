import io
import threading
from multiprocessing.shared_memory import ShareableList

from torch.multiprocessing import Queue, Lock, Value
from Cores.Processing import Chat_Process, Detection_Process, Depth_Process, ASR_Process, OCR_Process
from Cores.Threading import Amap_Thread, Timer_Thread

from PIL import Image
from Debug import logger


class Controller(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Controller, "_instance"):
            with Controller._instance_lock:
                if not hasattr(Controller, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    Controller._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return Controller._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self):
        print("Controller initializing...")

        (self.inLanguageQueue, self.outTextQueue, self.inAudioQueue,
         self.amapCallQueue, self.detectionCallQueue, self.ocrCallQueue) = (
            Queue(), Queue(), Queue(), Queue(), Queue(), Queue())
        '''
        inLanguageQueue：存放语音识别结果、函数回调的信息等需要LLM处理的文本，将会输入到ChatGLM
        outTextQueue：存放完成处理后的文本，将会输出到安卓设备，使用tts播放
        inAudioQueue：存放音频数据，将会输入到ASR做语音识别
        amapCallQueue：存放ChatGLM输出的高德函数调用信息，将会输入到Amap做函数调用
        detectionCallQueue：存放ChatGLM输出的物体检测的调用指令，将会输入到mmDetection做函数调用
        ocrCallQueue：存放ChatGLM输出的OCR的调用指令，将会输入到OCR做函数调用
        '''

        self.imageReadingLock, self.imageReaderCountLock, self.imageWritingLock, self.imageWriterCountLock = (
            Lock(), Lock(), Lock(), Lock())

        self.imageReaderCount, self.imageWriterCount = Value('i', 0), Value('i', 0)
        self.imageContainer = ShareableList([b' ' * 1024 * 1024 * 9])  # 9MB image max size
        self.imageContainer[0] = None  # imageContainer[0] is the image
        self.location_lat_lng = (23.04367093310192, 113.41183934259199)  # 初始位置在广州大学城

        self.detection_process = Detection_Process(self.imageContainer, self.imageReadingLock,
                                                   self.imageReaderCount, self.imageReaderCountLock,
                                                   self.imageWritingLock,
                                                   self.inLanguageQueue, self.outTextQueue, self.detectionCallQueue)
        self.depth_process = Depth_Process(self.imageContainer, self.imageReadingLock,
                                           self.imageReaderCount, self.imageReaderCountLock,
                                           self.imageWritingLock,
                                           self.outTextQueue)
        self.asr_process = ASR_Process(self.inAudioQueue, self.inLanguageQueue, self.amapCallQueue)
        self.ocr_process = OCR_Process(self.imageContainer, self.imageReadingLock,
                                       self.imageReaderCount, self.imageReaderCountLock,
                                       self.imageWritingLock,
                                       self.inLanguageQueue, self.ocrCallQueue)
        self.glm_process = Chat_Process(self.inLanguageQueue, self.outTextQueue,
                                        self.amapCallQueue, self.detectionCallQueue, self.ocrCallQueue)
        self.amap_thread = Amap_Thread(self.inLanguageQueue, self.outTextQueue, self.amapCallQueue)
        self.timer_thread = Timer_Thread(self.setImage, self.setLocation)

        self.start()
        logger.info("Controller initialized successfully.")

    def __del__(self):
        print("Controller stopping...")
        self.imageContainer.shm.close()
        self.imageContainer.shm.unlink()
        logger.info("Controller stopped successfully.")

    def start(self):

        self.detection_process.start()
        self.depth_process.start()
        self.asr_process.start()
        self.ocr_process.start()
        self.glm_process.start()

        self.amap_thread.start()
        self.timer_thread.start()

    def onUploadImage(self, image):

        try:
            _ = Image.open(io.BytesIO(image)).convert('RGB')
        except Exception as e:
            logger.error(f"error image uploaded {e}")
            return

        self.timer_thread.resetTimerImage()
        self.setImage(image)

    def setImage(self, image):
        self._beforeWriting()
        if image is None and self.imageContainer[0] is not None:
            logger.info("Image Reset to None")
        self.imageContainer[0] = image
        self._afterWriting()

    def setLocation(self, location_lat_lng=None):
        if location_lat_lng is None:
            if self.location_lat_lng != (23.04367093310192, 113.41183934259199):
                # 记录回到初始位置
                logger.info("Location Reset to 广州大学城")
            self.location_lat_lng = (23.04367093310192, 113.41183934259199)
            return

        lat = float(location_lat_lng[0])
        lng = float(location_lat_lng[1])
        self.location_lat_lng = (lat, lng)

    def _beforeWriting(self):
        self.imageWriterCountLock.acquire()
        if self.imageWriterCount.value == 0:
            self.imageWritingLock.acquire()
        self.imageWriterCount.value += 1
        self.imageWriterCountLock.release()
        self.imageReadingLock.acquire()

    def _afterWriting(self):
        self.imageReadingLock.release()
        self.imageWriterCountLock.acquire()
        self.imageWriterCount.value -= 1
        if self.imageWriterCount.value == 0:
            self.imageWritingLock.release()
        self.imageWriterCountLock.release()

    def onUploadAudio(self, audio):
        self.inAudioQueue.put(audio)

    def onRetrieveText(self, location_lat_lng=None):
        if location_lat_lng is not None:
            self.timer_thread.resetTimerLocation()
            self.setLocation(location_lat_lng)
        texts = []
        while not self.outTextQueue.empty():
            texts.extend(self.outTextQueue.get())
        if len(texts) > 0:
            logger.info(f"Retrieved text: {texts}")
        return texts

    def onUploadText(self, text):
        # 只用于debug
        self.inLanguageQueue.put([
            {
                "role": "system",
                "content": "你是AI智能眼镜，帮助视障群体与老年人的衣食住行。请仔细回答用户的提问。",
            },
            {
                "role": "user",
                "content": text,
            }
        ])
        logger.info(f"Uploaded text: {text}")


if __name__ == "__main__":
    Controller()
