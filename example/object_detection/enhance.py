import sys
sys.path.append("./MIRNet")

import numpy as np
import os
import argparse
from tqdm import tqdm

import torch.nn as nn
import torch
from torch.utils.data import DataLoader
import torch.nn.functional as F

from MIRNet.networks.MIRNet_model import MIRNet
from MIRNet.utils import load_checkpoint, save_img
from MIRNet.dataloaders.data_rgb import get_validation_data, get_test_data
from skimage import img_as_ubyte

def enhance():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    test_dataset = get_test_data("./MIRNet/test_images")
    test_loader = DataLoader(dataset=test_dataset, batch_size=1, shuffle=False, num_workers=8, drop_last=False)

    model_restoration = MIRNet()

    load_checkpoint(model_restoration, "./MIRNet/model_fivek.pth")
    print("===>Testing using weights: ", "./MIRNet/model_fivek.pth")

    model_restoration.cuda()

    model_restoration=nn.DataParallel(model_restoration)

    model_restoration.eval()

    with torch.no_grad():
        psnr_val_rgb = []
        for ii, data_test in enumerate(test_loader, 0):
            print(data_test[0].shape)
            #rgb_gt = data_test[0].cuda()
            rgb_noisy = data_test[0].cuda()
            filenames = data_test[1]
            rgb_restored = model_restoration(rgb_noisy)
            rgb_restored = torch.clamp(rgb_restored,0,1)

            #psnr_val_rgb.append(utils.batch_PSNR(rgb_restored, rgb_gt, 1.))

            #rgb_gt = rgb_gt.permute(0, 2, 3, 1).cpu().detach().numpy()
            rgb_noisy = rgb_noisy.permute(0, 2, 3, 1).cpu().detach().numpy()
            rgb_restored = rgb_restored.permute(0, 2, 3, 1).cpu().detach().numpy()

            for batch in range(len(rgb_restored)):
                enhanced_img = img_as_ubyte(rgb_restored[batch])
                save_img("./MIRNet/" + filenames[batch].split(".")[0] + '.jpg', enhanced_img)

if __name__ == "__main__":
    enhance()