import numpy as np
import torch

from Interfaces.DepthEstimation.LangSamClient import call_langsam, get_ground_idx
from Interfaces.DepthEstimation.convert_utils import get_minimal_depth_using_masks, get_coeff_from_relative_to_absolute, \
    get_absolute_depth_map_using_coeff, get_object_average_depth
from Interfaces.DepthEstimation.image_utils import image_process, resize_to_original_shape
from Interfaces.DepthEstimation.model import LDRN
from Interfaces.DepthEstimation.template import PROMPT_TEMPLATE


# construct model
def build_LapDepth(args, device):
    print('=> loading model..')
    model = LDRN(args)
    # if args.cuda and torch.cuda.is_available():
    #     Model = Model.cuda()
    # Model = torch.nn.DataParallel(Model)
    assert (args.model_dir != ''), "Expected pretrained model directory"
    # Model.load_state_dict(torch.load(args.model_dir))
    model_out_path = "/home/cike/weiyuancheng/LapDepth-release/pretrained/LDRN_KITTI_ResNext101_pretrained_data.pth"
    # torch.save(Model.module.state_dict(), model_out_path)
    # exit(-1) # 上方加载并保存DataParallel模型，方便下方直接加载保存的模型

    model.load_state_dict(torch.load(model_out_path, map_location=device))
    model.eval()
    # model = torch.compile(model)  # P100 is too old to support this
    return model.to(device)


# process one image
def LapDepth_forward(lapdepth_model, img, args, device):
    # img = Image.open(img_path) now img has already become Image.open(img_path)
    img, img_flip, org_h, org_w = image_process(img, args, device)
    with torch.no_grad():
        _, out = lapdepth_model(img)
        _, out_flip = lapdepth_model(img_flip)
    out_flip = torch.flip(out_flip, [3])
    out = (out + out_flip) * 0.5
    out = resize_to_original_shape(out, org_h, org_w)
    # out = out.cpu().numpy()
    return out


# VISUALIZATION
import matplotlib.pyplot as plt


def display_image_with_boxes(image, boxes, logits, estimated_distances, phrases, output_location):
    plt.figure(figsize=(12, 9))  # 设置图片大小

    plt.imshow(image)
    plt.title("Image with Bounding Boxes")
    plt.axis('off')

    for box, logit, distance, phrase in zip(boxes, logits, estimated_distances, phrases):
        if distance < 0:
            continue

        x_min, y_min, x_max, y_max = box
        confidence_score = round(logit.item(), 2)  # 转换logit为标量后进行四舍五入
        distance = round(distance.item(), 2)
        box_width = x_max - x_min
        box_height = y_max - y_min

        # 绘制边界框
        if distance > 500:
            rect = plt.Rectangle((x_min, y_min), box_width, box_height, fill=False, edgecolor='green', linewidth=2)
        else:
            rect = plt.Rectangle((x_min, y_min), box_width, box_height, fill=False, edgecolor='red', linewidth=2)
        plt.gca().add_patch(rect)

        # 添加置信度分数文本
        text_color = 'red' if distance < 500 else 'green'
        plt.text(x_min, y_min, f"Confidence: {confidence_score}\nObject: {phrase}\nDistance: {distance}", fontsize=8,
                 color=text_color, verticalalignment='top')

    plt.savefig(output_location, bbox_inches='tight')  # 保存图片
    plt.show()  # 显示图片


def get_ground_smallest_depth(relative_depth_map, phrases, masks):
    ground_mask_idx = get_ground_idx(phrases)
    ground_mask = masks[ground_mask_idx]
    ground_smallest_depth = get_minimal_depth_using_masks(relative_depth_map, ground_mask)
    return ground_smallest_depth


def convert_relative_depth_to_absolute_depth(relative_depth_map=None, masks=None, phrases=None):
    get_ground_smallest_relative_depth = get_ground_smallest_depth(relative_depth_map=relative_depth_map,
                                                                   phrases=phrases, masks=masks)
    coeff = get_coeff_from_relative_to_absolute(get_ground_smallest_relative_depth,
                                                180)  # set 180 as the relative depth of the object
    absolute_depth_map = get_absolute_depth_map_using_coeff(relative_depth_map, coeff)
    return absolute_depth_map


def calculate_absolute_depth_per_object(absolute_depth_map=None, masks=None, phrases=None):
    absolute_depths_per_objects = np.full_like(phrases, 0, dtype=float)
    for i in range(len(phrases)):
        if phrases[i] == 'ground':
            absolute_depths_per_objects[i] = -1
        else:
            average_depth = get_object_average_depth(absolute_depth_map, masks[i])
            absolute_depths_per_objects[i] = average_depth.item()
    return absolute_depths_per_objects


def get_absolute_depth_per_object(relative_depth_map=None, masks=None, phrases=None):
    assert relative_depth_map is not None, "Expected relative depth map"
    assert masks is not None, "Expected masks"
    assert phrases is not None, "Expected phrases"

    absolute_depth_map = convert_relative_depth_to_absolute_depth(relative_depth_map=relative_depth_map, masks=masks,
                                                                  phrases=phrases)
    absolute_depths_per_objects = calculate_absolute_depth_per_object(absolute_depth_map=absolute_depth_map,
                                                                      masks=masks, phrases=phrases)

    return absolute_depths_per_objects


# calculate the center of the object,
# if the center is on the left 1/3 side of the image, then the object is on the left side of the image
# if the center is on the right 1/3 side of the image, then the object is on the right side of the image
# if the center is on the middle 1/3 side of the image, then the object is on the middle side of the image
def get_direction_of_object(bbox, image_width):
    x_min, _, x_max, _ = bbox
    center_x = (x_min + x_max) / 2
    if center_x < image_width / 3:
        side = '左'
    elif center_x > image_width * 2 / 3:
        side = '右'
    else:
        side = '正'
    return side


def get_distance_of_object(distance):
    return '近' if distance < 500 else '远'


def get_language_prompt(object_names, bboxs, distances, image_width):
    prompts = []

    for i in range(len(object_names)):
        object = object_names[i]

        if object == 'ground':
            continue

        # calculate the center of the object
        side = get_direction_of_object(bboxs[i], image_width)
        # calculate the distance of the object
        distance = get_distance_of_object(distances[i])

        prompt = PROMPT_TEMPLATE.format(side, distance)
        prompts.append(prompt)

    return prompts


# MAIN FUNCTION
# output_location is used for debug only
def analyze_one_image(device, img=None, lapdepth_model=None, langsam_model=None, args=None,
                      prompt='ground . trashcan . people',
                      output_location=None):
    assert img is not None, "Expected image"
    assert lapdepth_model is not None, "Expected model"
    assert args is not None, "Expected args"
    assert prompt is not None, "Expected prompt"
    assert langsam_model is not None, "Expected langsam model"

    relative_depth_map = LapDepth_forward(lapdepth_model=lapdepth_model, img=img, args=args, device=device)
    boxes, logits, masks, phrases = call_langsam(langsam_model=langsam_model, img=img, prompt=prompt)

    relative_depth_map = relative_depth_map.to(masks.device)

    absolute_depth_per_object = get_absolute_depth_per_object(relative_depth_map=relative_depth_map, masks=masks,
                                                              phrases=phrases)

    language_prompt = get_language_prompt(object_names=phrases, bboxs=boxes, distances=absolute_depth_per_object,
                                          image_width=img.size[0])

    # debug only
    if output_location is not None:
        display_image_with_boxes(img, boxes, logits, absolute_depth_per_object, phrases, output_location)

    return language_prompt
