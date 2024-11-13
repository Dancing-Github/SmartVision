import torch


# This file contains the functions that are used to process the depth map
# including converting the depth map to absolute depth map
# and getting the average depth of the object in the image

# distance conversion related functions
def get_minimal_depth_using_masks(depth_out_ori, masks):
    # depth_out = depth_out_ori.clone()
    masks = masks.float()
    depth_out = depth_out_ori
    depth_out = depth_out * masks
    depth_out = depth_out.reshape(-1)
    # print(len(depth_out))
    # rewrite using torch, depth_out is a tensor
    depth_out = depth_out[depth_out != 0]
    # choose minimal 10% depth
    depth_out = torch.sort(depth_out)
    depth_out = depth_out[0][:int(len(depth_out[0]) * 0.1)]
    depth_out = depth_out.mean()

    return depth_out


def get_coeff_from_relative_to_absolute(ground_smallest_depth, relative_depth=180):
    return relative_depth / ground_smallest_depth


def get_absolute_depth_map_using_coeff(depth_out_ori, coeff):
    depth_out = depth_out_ori
    depth_out = depth_out * coeff
    return depth_out


def get_object_average_depth(absolute_depth_map, masks):
    # convert mask from True/False to 0/1 tensor
    masks = masks.float()
    depth_out = absolute_depth_map
    depth_out = depth_out * masks
    depth_out = depth_out.reshape(-1)
    depth_out = depth_out[depth_out != 0]
    # choose maximal 10% depth
    # depth_out is a tensor, rewrite using torch
    depth_out = torch.sort(depth_out)
    depth_out = depth_out[0][:int(len(depth_out[0]) * 0.1)]
    depth_out = depth_out.mean()

    # depth_out = np.sort(depth_out)
    # depth_out = depth_out[:int(len(depth_out)*0.1)]
    # depth_out = depth_out.mean()
    return depth_out
