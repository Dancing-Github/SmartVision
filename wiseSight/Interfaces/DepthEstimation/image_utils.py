import numpy as np
import torch
import torch.nn.functional as F
from PIL import PngImagePlugin
from torchvision import transforms


# image transformation
def normalize(img):
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    return normalize(img)


# utility functions
def resize_to_original_shape(img, org_h, org_w):
    img = F.interpolate(img, (org_h, org_w), mode='bilinear')
    return img


# image processing, i dont know why...
def image_process(img, args, device):
    if isinstance(img, PngImagePlugin.PngImageFile):
        img = img.convert('RGB')

    img = np.asarray(img, dtype=np.float32) / 255.0

    if img.ndim == 2:
        img = np.expand_dims(img, 2)
        img = np.repeat(img, 3, 2)
    img = img.transpose((2, 0, 1))
    img = torch.from_numpy(img).float()
    img = normalize(img)
    # if torch.cuda.is_available():
    # img = img.to()
    img = img.to(device)

    _, org_h, org_w = img.shape

    # new height and width setting which can be divided by 16
    img = img.unsqueeze(0)

    if args.pretrained == 'KITTI':
        new_h = 352
        new_w = org_w * (352.0 / org_h)
        new_w = int((new_w // 16) * 16)
        img = F.interpolate(img, (new_h, new_w), mode='bilinear')
    elif args.pretrained == 'NYU':
        new_h = 432
        new_w = org_w * (432.0 / org_h)
        new_w = int((new_w // 16) * 16)
        img = F.interpolate(img, (new_h, new_w), mode='bilinear')

    img_flip = torch.flip(img, [3])

    return img, img_flip, org_h, org_w
