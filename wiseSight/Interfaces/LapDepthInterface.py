import io
import threading
import time

from PIL import Image

from Interfaces.DepthEstimation import build_LapDepth, analyze_one_image
from Interfaces.DepthEstimation import build_langsam
# args
from Interfaces.DepthEstimation import construct_args


# os.environ['CUDA_VISIBLE_DEVICES'] = '2'
# sys.path.append('/home/cike/weiyuancheng/LapDepth-release')

def get_binary_stream_image(img_path):
    with open(img_path, 'rb') as file:
        input = file.read()
    return input


class LapDepthInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(LapDepthInterface, "_instance"):
            with LapDepthInterface._instance_lock:
                if not hasattr(LapDepthInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    LapDepthInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return LapDepthInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:0", langsam_model=None):
        self.args = construct_args()
        self.device = device
        if langsam_model is None:
            self.langsam_model = build_langsam(device)
        else:
            self.langsam_model = langsam_model
        self.model = build_LapDepth(self.args, device)
        assert self.model is not None, "Expected LapDepth model"

    def predict(self, img, prompt, output_location=None):

        res = analyze_one_image(lapdepth_model=self.model, langsam_model=self.langsam_model,
                                   img=img, device=self.device,
                                   output_location=output_location, args=self.args, prompt=prompt)
        return res


if __name__ == '__main__':
    lapdepth_model = LapDepthInterface()
    prompt = 'ground . trashcan . people'

    img = Image.open(io.BytesIO(get_binary_stream_image('/home/cike/weiyuancheng/LapDepth-release/assets/povt2.jpg')))

    # calculate a standard time used to predict
    start = time.time()
    guidence = lapdepth_model.predict(img, prompt)
    end = time.time()
    print('time used: ', end - start)
    print(guidence)

    # time used: 8.624093770980835 for a 330KB jpg image
    # {}前方{}处有一个障碍物
    # ['正前方近处有一个障碍物', '右前方远处有一个障碍物']
