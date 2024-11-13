import json
import sys
from typing import Optional

import math
import mmcv
import torch
from mmdet.apis import init_detector, inference_detector


class mmDectionModel:
    def __init__(self, device):
        sys.path.append("/home/cike/xyq/mmdetction")  # 将项目根目录添加到环境变量中
        self.device = device
        self.config_file = "/home/cike/xyq/mmdetction/projects/Detic_new/configs/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis.py"
        self.checkpoint_file = '/home/cike/xyq/mmdetction/checkpoints/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis-ec91245d.pth'
        self.model = init_detector(self.config_file, self.checkpoint_file, device=self.device, palette='random')
        self.model = torch.compile(self.model)  # P100 is too old to support this

    def Detector(self, input, pred_score_thr=0.5, text_prompt: Optional[str] = None):
        # 基本的物体识别接口，input为图片(numpy.array格式)，pred_score_thr代表识别阈值，text_prompt为需要识别的物体，为空则全部都识别
        input = mmcv.imfrombytes(input)
        object_list = inference_detector(self.model, imgs=input)
        object_list = (vars(object_list))["_pred_instances"]
        result = []
        filtered_values = [value for value in object_list["scores"] if value > pred_score_thr]
        for i in range(len(filtered_values)):
            if text_prompt == None or (object_list['label_names'][i] in text_prompt):
                result.append({'label_names': object_list['label_names'][i],
                               'scores': object_list['scores'][i],
                               'box': object_list['bboxes'][i]
                               })
        # result包含每个被识别物体的标签，概率，box
        return result

    def busDetector(self, input):
        # 用于识别公交车的位置，其中bus_box四个值分别为公交车左下角和右下角的坐标，input为图片(numpy.array格式)
        bus_box = self.Detector(input=input, text_prompt=['bus_(vehicle)'])
        if not bus_box:
            return '前方无公交车'
        else:
            bus_box = bus_box[0]['box']
        return bus_box

    def congestionDetector(self, input):
        car_num = len(self.Detector(input=input, text_prompt=['car_(automobile)']))
        person_num = len(self.Detector(input=input, text_prompt=['person']))
        if car_num == 0 and person_num == 0:
            return '马路上没人没车，放心行走'
        elif car_num>=12 and person_num>=12:
            return '马路上人车拥挤，小心避让'

        if car_num < 4:
            car_output = '车辆较少'
        elif car_num < 12:
            car_output = '车辆较多'
        else:
            car_output = '车辆很多'

        if person_num < 4:
            person_output = '行人较少'
        elif person_num < 12:
            person_output = '行人较多'
        else:
            person_output = '行人很多'
        return f"马路上{person_output}，{car_output}，请注意安全"

    def distance_between_points(self, x1, y1, x2, y2):
        # 用于检测物体间的距离，用于重要物体位置提示中
        return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def square_center(self, x, y, width, height):
        # 用于检测物体中心位置，用于重要物体位置提示中
        return (x + width) / 2, (y + height) / 2

    def keyObjectDetector(self, input, scene, key_text, output_dir):
        # 用于维护重要物体的位置，检测到重要物体则保存
        # result = False
        json_data = []

        output = self.Detector(input=input)
        input = mmcv.imfrombytes(input)
        found = set()
        label_list = [value['label_names'] for value in output if (value["label_names"] in key_text)]
        for word in key_text:
            if word in label_list:
                mmcv.imwrite(input, output_dir + word + '.jpg')
                found.add(word)
                # result = True

        if len(found) == 0:
            return found

        for word in found:
            key_box = [value for value in output if (value["label_names"] == word)][0]['box']
            box_list = [value for value in output if (value["label_names"] != word)]
            distance = []
            x0, y0 = self.square_center(key_box[0], key_box[1], key_box[2], key_box[3])
            for i in range(len(box_list)):
                x1, y1 = self.square_center(box_list[i]['box'][0], box_list[i]['box'][1], box_list[i]['box'][2],
                                            box_list[i]['box'][3])
                distance.append({
                    'distance': self.distance_between_points(
                        x0, y0, x1, y1
                    ),
                    "center": [int(x1), int(y1)],
                    'label': box_list[i]['label_names']
                })
            sorted_array = sorted(distance, key=lambda x: x['distance'])
            # 去除同一物体的多种识别结果
            unique_distance = []
            distance_values = set()
            for d in sorted_array:
                distance_value = d['distance']
                if distance_value not in distance_values and distance_value != 0:
                    distance_values.add(distance_value)
                    unique_distance.append(d)
            # 去除多个同一物体
            unique_label = []
            label_values = set()
            for d in unique_distance:
                key_value = d['label']
                if key_value not in label_values:
                    label_values.add(key_value)
                    unique_label.append(d)
            # round保存了每个物体距离关键物体的距离和坐标
            json_data.append({"name": word, 'scene': scene, "x0": int(x0), "y0": int(y0), "objects": unique_label})

        with open(output_dir + 'data.json', encoding="utf-8") as f:
            old_data = json.load(f)
            for one in old_data:
                if one['name'] not in found:
                    json_data.append(one)
        with open(output_dir + 'data.json', 'w', encoding="utf-8") as f:
            json.dump(json_data, f)

        return found
