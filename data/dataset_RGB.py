import os

import albumentations as A
import numpy as np
import torchvision.transforms.functional as F
from PIL import Image
from torch.utils.data import Dataset


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in ['jpeg', 'JPEG', 'jpg', 'png', 'JPG', 'PNG', 'gif'])


class DataLoaderTrain(Dataset):
    def __init__(self, rgb_dir, inp='input', target='target', img_options=None):
        super(DataLoaderTrain, self).__init__()

        inp_files = sorted(os.listdir(os.path.join(rgb_dir, inp)))
        tar_files = sorted(os.listdir(os.path.join(rgb_dir, target)))
        # mas_files = sorted(os.listdir(os.path.join(rgb_dir, 'mask')))

        self.inp_filenames = [os.path.join(rgb_dir, inp, x) for x in inp_files if is_image_file(x)]
        self.tar_filenames = [os.path.join(rgb_dir, target, x) for x in tar_files if is_image_file(x)]
        # self.mas_filenames = [os.path.join(rgb_dir, 'mask', x) for x in mas_files if is_image_file(x)]

        self.img_options = img_options
        self.sizex = len(self.tar_filenames)  # get the size of target

        self.transform = A.Compose([
            A.Resize(height=img_options['h'], width=img_options['w']),
            A.HorizontalFlip(p=0.3),
            A.VerticalFlip(p=0.3),
            A.RandomRotate90(p=0.3), ],
            additional_targets={
                'target': 'image',
            }
        )

    def __len__(self):
        return self.sizex

    def __getitem__(self, index):
        index_ = index % self.sizex

        inp_path = self.inp_filenames[index_]
        tar_path = self.tar_filenames[index_]

        inp_img = Image.open(inp_path).convert('L')
        tar_img = Image.open(tar_path).convert('L')

        inp_img = np.array(inp_img)
        tar_img = np.array(tar_img)

        transformed = self.transform(image=inp_img, target=tar_img)

        inp_img = F.to_tensor(transformed['image'])
        tar_img = F.to_tensor(transformed['target'])

        filename = os.path.splitext(os.path.split(tar_path)[-1])[0]

        return inp_img, tar_img, filename


class DataLoaderVal(Dataset):
    def __init__(self, rgb_dir, inp='input', target='target', img_options=None):
        super(DataLoaderVal, self).__init__()

        inp_files = sorted(os.listdir(os.path.join(rgb_dir, inp)))
        tar_files = sorted(os.listdir(os.path.join(rgb_dir, target)))

        self.inp_filenames = [os.path.join(rgb_dir, inp, x) for x in inp_files if is_image_file(x)]
        self.tar_filenames = [os.path.join(rgb_dir, target, x) for x in tar_files if is_image_file(x)]

        self.img_options = img_options
        self.sizex = len(self.tar_filenames)  # get the size of target

        self.transform = A.Compose([
            A.Resize(height=img_options['h'], width=img_options['w']), ],
            additional_targets={
                'target': 'image',
            }
        )

    def __len__(self):
        return self.sizex

    def __getitem__(self, index):
        index_ = index % self.sizex

        inp_path = self.inp_filenames[index_]
        tar_path = self.tar_filenames[index_]

        inp_img = Image.open(inp_path).convert('L')
        tar_img = Image.open(tar_path).convert('L')

        if not self.img_options['ori']:
            inp_img = np.array(inp_img)
            tar_img = np.array(tar_img)

            transformed = self.transform(image=inp_img, target=tar_img)

            inp_img = transformed['image']
            tar_img = transformed['target']

        inp_img = F.to_tensor(inp_img)
        tar_img = F.to_tensor(tar_img)

        filename = os.path.split(tar_path)[-1]

        return inp_img, tar_img, filename
