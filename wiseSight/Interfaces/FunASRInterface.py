import os
import tempfile
import threading

import ffmpeg
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from Debug import logger


class FunASRInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(FunASRInterface, "_instance"):
            with FunASRInterface._instance_lock:
                if not hasattr(FunASRInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    FunASRInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return FunASRInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:2"):  # 好像只能用cuda 0，设置其他的设备也是cuda 0

        # Loading the UniASR model
        self.inference_16k_pipline = pipeline(
            task=Tasks.auto_speech_recognition,
            model='/home/cike/LJJ/FunASR/model/speech_UniASR-large_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline',
            device=device,
        )
        logger.info(f"Model-UniASR loaded successfully on device: ${self.inference_16k_pipline.device}")

        # Load the punc_ct model
        self.inference_pipline = pipeline(
            task=Tasks.punctuation,
            model='/home/cike/LJJ/FunASR/model/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
            model_revision="v1.1.7",
            device=device,
        )
        logger.info(f"Model-punc_ct loaded successfully on device: ${self.inference_pipline.device}")

    def inferFunction(self, input):

        # 转换格式
        data = self.convert_format(input)
        rec_result = self.inference_16k_pipline(data)
        result = self.inference_pipline(text_in=rec_result['text'])
        return result['text']

    def convert_format(self, input):
        # 生成一个临时文件名，扩展名为 .amr
        with tempfile.NamedTemporaryFile(suffix='.amr') as f:
            f.write(input)
            # 导出为WAV格式的临时文件
            ffmpeg.input(f.name).output('./data/temp.wav').run()

        # 读取所有二进制数据
        with open('./data/temp.wav', 'rb') as file:
            data = file.read()
        os.remove('./data/temp.wav')
        return data

    # example


if __name__ == "__main__":
    # 调用例子
    testModule = FunASRInterface()
    # 打开音频文件并以二进制模式读取
    with open('/home/cike/LJJ/FunASR/test-wav/FinalAudio(1).amr', 'rb') as file:
        input = file.read()
    output = testModule.inferFunction(input)
    print(output)
