import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torchvision import models
from torchvision import transforms


class SingleImageDataset(Dataset):
    def __init__(self, img, transform=None):
        self.img = img
        self.transform = transform

    def __len__(self):
        return 1  # 因为只有一个图片

    def __getitem__(self, idx):
        if self.transform:
            img = self.transform(self.img)
            return img
        else:
            return self.img


class SceneModel:
    def __init__(self, device):
        self.model = models.densenet201(weights=True)
        self.model.classifier = nn.Linear(1920, 67, bias=True)
        model_wts = torch.load("/home/cike/xyq/home_scene_5.pkl", map_location=device)
        self.model.load_state_dict(model_wts)
        self.model.eval()
        self.model = torch.compile(self.model)  # P100 is too old to support this

        # self.optimizer = optim.SGD(self.model.parameters(), lr=0.001)
        self.categories = ["bathroom", "bedroom", "dining_room", "kitchen", "living_room"]
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

    def Detector(self, input):
        input = Image.fromarray(np.uint8(input))
        single_image_dataset = SingleImageDataset(input, transform=self.transform)

        # 创建 DataLoader，设置 batch_size 为 1
        data_loader = DataLoader(single_image_dataset, batch_size=1)

        # 遍历 DataLoader 中的每个批次（实际上只有一个批次）
        for images in data_loader:
            # 在这里执行你的处理步骤，images 包含了单个图片的张量
            # images=images.cuda()
            # self.optimizer.zero_grad()
            with torch.no_grad():
                outputs = self.model(images)
                _, preds = torch.max(outputs.data, 1)
                return self.categories[preds]
