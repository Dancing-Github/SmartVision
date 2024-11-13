import json
import threading
from pathlib import Path

import mmcv

from Interfaces.ObjectDetection import SceneModel
from Interfaces.ObjectDetection import TrafficLightModel
from Interfaces.ObjectDetection import mmDectionModel


class DetectionInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(DetectionInterface, "_instance"):
            with DetectionInterface._instance_lock:
                if not hasattr(DetectionInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    DetectionInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return DetectionInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:2"):
        # 初始化模型
        # device = device if torch.cuda.is_available() else 'cpu'
        self.dectionModel = mmDectionModel(device=device)
        self.sceneModel = SceneModel(device=device)
        self.trafficLightModel = TrafficLightModel()

    def busDetector(self, input):
        # 用于识别公交车的位置，其中bus_box四个值分别为公交车左下角和右下角的坐标，input为图片(numpy.array格式)
        return self.dectionModel.busDetector(input)

    def trafficLightDetector(self, input):
        # 用于识别红绿灯颜色，input为图片(numpy.array格式)
        light_box = self.dectionModel.Detector(input=input, text_prompt=['traffic_light'])
        input = mmcv.imfrombytes(input)
        if not light_box:
            return '前方没有红绿灯'
        else:
            light_box = light_box[0]['box']
        # light_box为红绿灯的位置
        input = input[int(light_box[1]):int(light_box[3]), int(light_box[0]):int(light_box[2])]
        return self.trafficLightModel.inferFunction(input)  # 返回结果

    def congestionDetector(self, input):
        return self.dectionModel.congestionDetector(input)

    def keyObjectDetector(self, input, key_text=None, output_dir='./data/'):
        # 用于维护重要物体的位置，检测到重要物体则保存
        if key_text is None:
            key_text = ['key', 'wallet', 'cellular_telephone', 'remote']
        scene = self.sceneModel.Detector(input=mmcv.imfrombytes(input))
        return self.dectionModel.keyObjectDetector(input, scene, key_text, output_dir)

    # def _distance_between_points(self, x1, y1, x2, y2):
    #     # 用于检测物体间的距离，用于重要物体位置提示中
    #     return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
    #
    # def _square_center(self, x, y, width, height):
    #     # 用于检测物体中心位置，用于重要物体位置提示中
    #     return (x + width) / 2, (y + height) / 2

    def keyObject_LocationHint(self, text_object='key', root_dir="./data/"):


        # 用于检测重要物体位置，text_object为物体名称
        path = Path(root_dir + 'data.json')
        if not path.exists():
            return "找不到物体"

        with open(root_dir + 'data.json', 'r') as f:
            loaded_data = json.load(f)
        # 初始化索引为 None（表示未找到）
        index_key = None

        # 遍历字典数组，查找 name=1 的项
        for index, item in enumerate(loaded_data):
            if item.get('name') == text_object:
                index_key = index
                break  # 找到后退出循环
        if index_key == None:
            return "找不到物体"
        result = f"根据给出的信息描述{text_object}所在场景以及相对位置.场景: {loaded_data[index_key]['scene']}.{text_object}坐标为({int(loaded_data[index_key]['x0'])},{int(loaded_data[index_key]['y0'])}) {text_object}周围物体坐标为："
        for object in loaded_data[index_key]['objects']:
            result = result + f" {object['label']}({object['center'][0]},{object['center'][1]}) "
        return result
