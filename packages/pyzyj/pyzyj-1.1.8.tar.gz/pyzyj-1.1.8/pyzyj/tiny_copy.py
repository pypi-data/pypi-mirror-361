# -*- coding: utf-8 -*-
"""
@Time: 2024-01-30 13:32
@Auth: xjjxhxgg
@File: tiny_copy.py
@IDE: PyCharm
@Motto: xhxgg
"""
import math
import os
import random
from typing import Iterable
import numpy as np
from pycocotools.coco import COCO
import cv2
import json


'''
for copy tiny targets several times to make the dataset more balanced
1. copy the targets to other places in the same image and copy the labels
2. copy the entire image and copy the labels, that is to say, the image is copied several times
    and put into a new image which is of the size x × y 
    where x is the times of copied images in the vertical direction
    and y is the times of copied images in the horizontal direction 
'''


def target_copy(img_path, ann_path, save_path, times=2, parser: callable = None,
                data_format: str = 'yolo', new_name=None, copy_type='tgt', new_img_size=None):
    """
    copy the targets to other places in the same image and copy the labels
    :param img_path: the path of image
    :param ann_path: the path of annotation file
    :param save_path: the directory to save the new image and annotation file
    :param times: the times of copied targets. If copy_type == 'img', times, which is a Union[list,tuple] for [x,y] or number for y=x=sqrt(times), is the times of copied images
        while if copy_type == 'tgt', times,which is a single number, is the times of copied targets, and if there are n targets in the image,
        each target will be copied (times/n) times, if times/n is less than 1, each target will be copied for times times.
    :param parser: if ann_path is xml, parser is required, which is a callable function and returns a list of bbox
     like [{'name':name, 'bbox':[xmin,ymin,xmax,ymax]},...].
     A simple parser is provided in format.py
    :param data_format: the format of annotation file which should be in ['custom', 'yolo', 'coco'].
        If format is 'custom', a  parser is needed which returns the same format as above.
    :param new_name: the new name of the new image. If None, the new name will be the same as the old one.
        It can None if save_path is not a dir.
    :param copy_type: It must be in ['tgt','img'] which relatively mean :
        1. copy the targets to other places in the same image and copy the labels
        2. copy the entire image and copy the labels, that is to say, the image is copied several times
            and put into a new image which is of the size x × y
            where x is the times of copied images in the vertical direction
            and y is the times of copied images in the horizontal direction
    :param new_img_size: Only used when copy_type is 'img'.
        The size of the new image, which is a number, the factor of the old image size, like -2,-1, 1, 2, 3, 4, ...
        where -2 means 1/2 of the old image size, 2 means 2 times of the old image size.
        If None, the new image size will not be changed after copying,
        that is if [x,y]=[2,3] and original img size is [w,h] then the new img is of size [2w,3h].
        If times is a number, the new image size will be [w*sqrt(times),h*sqrt(times)],
        and if new_img_size is a -sqrt(times), the new image size will be the same as the old one.

    :return:
    """
    old_img_name = os.path.basename(img_path)
    old_img = cv2.imread(img_path)
    old_img_height = old_img.shape[0]
    old_img_width = old_img.shape[1]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if new_name is None:
        new_name = old_img_name
    save_img_path = os.path.join(save_path, new_name)
    save_ann_path = os.path.join(save_path, new_name.split('.')[0] + '.txt')

    img = old_img.copy()

    random_gen = random.Random()
    random_gen.seed(0)

    if copy_type == 'tgt':
        if data_format == 'yolo':
            bboxes = parser(ann_path, old_img_width, old_img_height)
            if len(bboxes) == 0:
                raise Exception('No bbox found in the annotation file')
            target_num = len(bboxes)
            each_target_times = times // target_num
            if each_target_times == 0:
                each_target_times = times
            targets_to_copy = []
            for i in range(times):
                for bbox in bboxes:
                    name = bbox['name']
                    bbox = bbox['bbox']
                    xmin, ymin, xmax, ymax = bbox
                    target = old_img[ymin:ymax, xmin:xmax, :]
                    for j in range(each_target_times):
                        targets_to_copy.append({'name': name, 'target': target})
            for target in targets_to_copy:
                name = target['name']
                target = target['target']
                # random position to put the target in the image
                # and copy the label to the new annotation file and save the new image
                new_x_min = random_gen.randint(0, old_img_width - target.shape[1])
                new_y_min = random_gen.randint(0, old_img_height - target.shape[0])
                new_x_max = new_x_min + target.shape[1]
                new_y_max = new_y_min + target.shape[0]
                img[new_y_min:new_y_max, new_x_min:new_x_max, :] = target
                new_cx = (new_x_min + new_x_max) / 2
                new_cy = (new_y_min + new_y_max) / 2
                new_w = new_x_max - new_x_min
                new_h = new_y_max - new_y_min
                # new_anns.append([name, new_cx / old_img_width, new_cy / old_img_height, new_w / old_img_width, new_h / old_img_height])
                with open(save_ann_path, 'a') as f:
                    f.write(
                        f'{name} {new_cx / old_img_width} {new_cy / old_img_height} {new_w / old_img_width} {new_h / old_img_height}\n')

            cv2.imwrite(save_img_path, img)


        elif data_format == 'coco':
            save_ann_path = save_ann_path.replace('txt','json')
            pass
        else:
            pass
    elif copy_type == 'img':
        if isinstance(times, int):
            x_times, y_times = int(math.sqrt(times)), int(math.sqrt(times))
        elif isinstance(times, Iterable):
            x_times, y_times = times

        new_img_width = old_img_width * y_times
        new_img_height = old_img_height * x_times
        img = np.ones((new_img_height, new_img_width, 3), dtype=np.uint8) * 255
        for i in range(x_times):
            for j in range(y_times):
                img[i * old_img_height:(i + 1) * old_img_height, j * old_img_width:(j + 1) * old_img_width, :] = old_img
        if new_img_size is not None:
            if new_img_size < 0:
                new_img_size = 1 / -new_img_size
            img = cv2.resize(img, (int(new_img_width * new_img_size), int(new_img_height * new_img_size)))
        cv2.imwrite(save_img_path, img)

        if data_format == 'yolo':
            bboxes = parser(ann_path, old_img_width, old_img_height)
            for i in range(x_times):
                for j in range(y_times):
                    for bbox in bboxes:
                        name = bbox['name']
                        bbox = bbox['bbox']
                        xmin, ymin, xmax, ymax = bbox
                        new_x_min = j * old_img_width + xmin
                        new_y_min = i * old_img_height + ymin
                        new_x_max = j * old_img_width + xmax
                        new_y_max = i * old_img_height + ymax
                        with open(save_ann_path, 'a') as f:
                            f.write(
                                f'{name} {(new_x_min + new_x_max) / 2 / new_img_width} {(new_y_min + new_y_max) / 2 / new_img_height} {(new_x_max - new_x_min) / new_img_width} {(new_y_max - new_y_min) / new_img_height}\n')
        elif data_format == 'coco':
            save_ann_path = save_ann_path.replace('txt', 'json')
            coco = COCO(ann_path)
            imgs = coco.imgs
            img_ids = None
            for img in imgs.values():
                if img['file_name'] == old_img_name:
                    img_ids = img['id']
                    break
            ann_ids = coco.getAnnIds(img_ids)
            anns_ = coco.loadAnns(ann_ids)
            max_ann_id = max(coco.getAnnIds())
            next_ann_id = max_ann_id + 1
            for i in range(x_times):
                for j in range(y_times):
                    for ann_id in ann_ids:
                        ann = coco.anns[ann_id].copy()
                        bbox = ann['bbox']
                        new_x_min = j * old_img_width + bbox[0]
                        new_y_min = i * old_img_height + bbox[1]
                        new_w = bbox[2]
                        new_h = bbox[3]
                        ann['bbox'] = [new_x_min * new_img_size, new_y_min * new_img_size, new_w * new_img_size, new_h * new_img_size]
                        ann['image_id'] = img_ids
                        ann['id'] = next_ann_id
                        ann['area'] = new_w * new_h * new_img_size * new_img_size
                        coco.anns[next_ann_id] = ann
                        next_ann_id += 1

            for ann_id in ann_ids:
                coco.anns.pop(ann_id)
            coco.imgs[img_ids]['width'] = int(new_img_width * new_img_size)
            coco.imgs[img_ids]['height'] = int(new_img_height * new_img_size)
            anns = {'images': list(coco.imgs.values()), 'annotations': list(coco.anns.values()), 'categories': list(coco.cats.values()), 'info': [], 'licenses': []}
            with open(save_ann_path, 'w') as f:
                json.dump(anns, f) # [ann for ann in  anns['annotations'] if ann['id']==5415] max([ann['id'] for ann in  anns['annotations']])

        else:
            pass
    else:
        raise Exception('copy_type must be in [\'tgt\',\'img\']')


if __name__ == '__main__':
    from format import yolo_parser
    from visualize import visualize
    #
    # img_path = r'F:\GD\dataset\coco128\images\train2017\000000000025.jpg'
    # ann_path = r'F:\GD\dataset\coco128\labels\train2017\000000000025.txt'
    # # target_copy(img_path, ann_path, '.', times=2, parser=yolo_parser, data_format='yolo', new_name=None, copy_type='tgt')
    # target_copy(img_path, ann_path, '.', times=4, parser=yolo_parser, data_format='yolo', copy_type='img', new_img_size=-2)
    # visualize('000000000025.jpg', '000000000025.txt')
    # coco = COCO(r'F:\GD\dataset\UAVDT\annotations\M0101.json')
    # js = json.load(open(r'F:\GD\dataset\UAVDT\annotations\M0101.json', 'r'))
    # print()
    # ann_path = r'F:\GD\dataset\HIT-UAV\annotations\train.json'
    # img_path = r'F:\GD\dataset\HIT-UAV\images\train\0_60_30_0_01611.jpg'
    ann_path = r'F:\GD\dataset\UAVDT\annotations\M0101.json'
    img_path = r'F:\GD\dataset\UAVDT\images\M0101-img000008.jpg'
    save_path = r'..'
    target_copy(img_path, ann_path, '..', times=4, data_format='coco', copy_type='img', new_img_size=-2)
    visualize('M0101-img000008.jpg', 'M0101-img000008.json')
    # visualize(img_path, ann_path)