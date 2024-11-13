import torch
import torch.backends.cudnn as cudnn


class Args:
    def __init__(
            self, img_dir="/home/cike/weiyuancheng/LapDepth-release/assets/povt1.jpg", img_folder_dir=None, seed=0,
            encoder="ResNext101", pretrained="KITTI", norm="BN", n_Group=32, reduction=16, act="ReLU",
            max_depth=80.0, lv6=False, cuda=True, rank=0, gpu_num=0):
        self.img_dir = img_dir
        self.img_folder_dir = img_folder_dir
        self.seed = seed
        self.encoder = encoder
        self.pretrained = pretrained
        self.norm = norm
        self.n_Group = n_Group
        self.reduction = reduction
        self.act = act
        self.max_depth = max_depth
        self.lv6 = lv6
        self.cuda = cuda
        self.rank = rank
        self.gpu_num = gpu_num
        self.model_dir = "/home/cike/weiyuancheng/LapDepth-release/pretrained/LDRN_KITTI_ResNext101_pretrained_data.pkl"


def construct_args():
    args = Args()

    assert (args.img_dir is not None) or (
            args.img_folder_dir is not None), "Expected name of input image file or folder"

    if args.cuda and torch.cuda.is_available():
        # os.environ["CUDA_VISIBLE_DEVICES"]= args.gpu_num
        cudnn.benchmark = True
        print('=> on CUDA')
    else:
        print('=> on CPU')

    if args.pretrained == 'KITTI':
        args.max_depth = 80.0
    elif args.pretrained == 'NYU':
        args.max_depth = 10.0

    return args
