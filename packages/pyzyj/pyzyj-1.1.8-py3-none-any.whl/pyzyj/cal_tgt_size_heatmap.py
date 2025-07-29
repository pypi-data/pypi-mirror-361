# -*- encoding: utf-8 -*-
"""
@Time: 2024-03-11 19:26
@Auth: xjjxhxgg
@File: cal_tgt_size_heatmap.py
@IDE: PyCharm
@Motto: xhxgg
"""
import os
from typing import Union

import cv2
from .format import yolo_parser, coco_parser, yolo_obb_parser
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import Counter
import numpy as np
import seaborn as sb
import pandas as pd


def yolo_cal_tgt_size_dist(yolo_root=r'/data/ll/code/sod/YOLOv8_With_ODConv/dataset/3x3',s=None, box_format='hbb'):
    def __get_sizes(imgs, img_root, lbl_root, box_format='hbb'):
        size_cnt_map = {}
        sizes = []
        hw_pair = []
        if box_format == 'hbb':
            for img in imgs:
                img_path = fr'{img_root}/{img}'
                lbl_path = fr'{lbl_root}/{img.replace("jpg", "txt")}'
                img = cv2.imread(img_path)
                h, w, _ = img.shape
                boxes = yolo_parser(lbl_path)
                for nb in boxes:
                    box = nb['bbox']
                    size = int(box[2] * box[3] * w * h)
                    if size not in size_cnt_map:
                        size_cnt_map[size] = 0
                    size_cnt_map[size] += 1
                    sizes.append(size)
                    bw = int(box[2] * w)
                    bh = int(box[3] * h)
                    hw_pair.append((bh, bw))
        elif box_format == 'obb':
            for img in imgs:
                img_path = fr'{img_root}/{img}'
                lbl_path = fr'{lbl_root}/{img.replace("jpg", "txt")}'
                img = cv2.imread(img_path)
                h, w, _ = img.shape
                boxes = yolo_obb_parser(lbl_path)
                for nb in boxes:
                    box = nb['obb']
                    size = int(box[-1] * box[-2] * w * h)
                    if size not in size_cnt_map:
                        size_cnt_map[size] = 0
                    size_cnt_map[size] += 1
                    sizes.append(size)
                    bw = int(box[2] * w)
                    bh = int(box[3] * h)
                    hw_pair.append((bh, bw))
        else:
            raise ValueError(f'box_format {box_format} not supported, only support hbb and obb')
        return sizes, size_cnt_map, hw_pair

    has_train = 'train' in os.listdir(f'{yolo_root}/images') and 'train' in os.listdir(f'{yolo_root}/labels')
    has_test = 'test' in os.listdir(f'{yolo_root}/images') and 'test' in os.listdir(f'{yolo_root}/labels')
    has_val = 'val' in os.listdir(f'{yolo_root}/images') and 'val' in os.listdir(f'{yolo_root}/labels')
    if not has_train and not has_test and not has_val:
        raise ValueError('No train or test set found')
    if s is not None:
        img_root = fr'{yolo_root}/images/{s}'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/{s}'
        sizes, size_cnt_map, hw_pair = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
    elif not has_train and not has_val:
        img_root = fr'{yolo_root}/images/test'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/test'
        sizes, size_cnt_map, hw_pair = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
    elif not has_test and not has_val:
        img_root = fr'{yolo_root}/images/train'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/train'
        sizes, size_cnt_map, hw_pair = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
    elif not has_test and not has_train:
        img_root = fr'{yolo_root}/images/val'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/val'
        sizes, size_cnt_map, hw_pair = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
    elif not has_val:
        img_root = fr'{yolo_root}/images/train'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/train'
        sizes_train, size_cnt_map_train, hw_pair_train = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        img_root = fr'{yolo_root}/images/test'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/test'
        sizes_test, size_cnt_map_test, hw_pair_test = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        sizes = sizes_train + sizes_test
        size_cnt_map = size_cnt_map_train
        for k, v in size_cnt_map_test.items():
            if k not in size_cnt_map:
                size_cnt_map[k] = 0
            size_cnt_map[k] += v
        hw_pair = hw_pair_train + hw_pair_test
    elif not has_test:
        img_root = fr'{yolo_root}/images/train'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/train'
        sizes_train, size_cnt_map_train, hw_pair_train = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        img_root = fr'{yolo_root}/images/val'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/val'
        sizes_val, size_cnt_map_val, hw_pair_val = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        sizes = sizes_train + sizes_val
        size_cnt_map = size_cnt_map_train
        for k, v in size_cnt_map_val.items():
            if k not in size_cnt_map:
                size_cnt_map[k] = 0
            size_cnt_map[k] += v
        hw_pair = hw_pair_train + hw_pair_val
    elif not has_train:
        img_root = fr'{yolo_root}/images/test'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/test'
        sizes_test, size_cnt_map_test, hw_pair_test = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        img_root = fr'{yolo_root}/images/val'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/val'
        sizes_val, size_cnt_map_val, hw_pair_val = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        sizes = sizes_test + sizes_val
        size_cnt_map = size_cnt_map_test
        for k, v in size_cnt_map_val.items():
            if k not in size_cnt_map:
                size_cnt_map[k] = 0
            size_cnt_map[k] += v
        hw_pair = hw_pair_test + hw_pair_val
    else:
        img_root = fr'{yolo_root}/images/train'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/train'
        sizes_train, size_cnt_map_train, hw_pair_train = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        img_root = fr'{yolo_root}/images/test'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/test'
        sizes_test, size_cnt_map_test, hw_pair_test = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        img_root = fr'{yolo_root}/images/val'
        imgs = os.listdir(img_root)
        lbl_root = fr'{yolo_root}/labels/val'
        sizes_val, size_cnt_map_val, hw_pair_val = __get_sizes(imgs, img_root, lbl_root, box_format=box_format)
        sizes = sizes_train + sizes_test + sizes_val
        size_cnt_map = size_cnt_map_train
        for k, v in size_cnt_map_test.items():
            if k not in size_cnt_map:
                size_cnt_map[k] = 0
            size_cnt_map[k] += v
        for k, v in size_cnt_map_val.items():
            if k not in size_cnt_map:
                size_cnt_map[k] = 0
            size_cnt_map[k] += v
        hw_pair = hw_pair_train + hw_pair_test + hw_pair_val
    return sizes, size_cnt_map, hw_pair




def cal_tgt_size_dist(*,res='c', yolo_root=None, coco_root=None, format='yolo',s=None, box_format='hbb'):
    """
    :param res: If res is set to 'c', return the size_cnt_map,
    else return the sizes list, size cnt map, hieght width pair
    :param yolo_root:
    :param coco_root:
    :param format:
    :return:
    """
    if format == 'yolo':
        sizes, size_cnt_map, hw_pair = yolo_cal_tgt_size_dist(yolo_root,s, box_format=box_format)
    elif format == 'coco':
        raise NotImplementedError
    if res == 'c':
        return size_cnt_map
    return sizes, size_cnt_map, hw_pair


def gen_heatmap(*, res='a', base=None,yolo_root=None, coco_root=None,
                filename='heatmap.png', threshold: Union[list, tuple, int, float] = None,s=None, box_format='hbb'):
    """
    :param base: If base is not None, the width and height will be rounded
    to the maximum multiple of base less than the original width and height
    :param filename:
    :param threshold: The maximum width and height to be shown in the heatmap
    :return:
    """

    format = 'yolo'
    if yolo_root is None and coco_root is None:
        raise ValueError('yolo_root and coco_root cannot be both None')
    if yolo_root is not None and coco_root is not None:
        raise ValueError('yolo_root and coco_root cannot be both not None')
    if yolo_root is not None:
        _, _, hw_pair = cal_tgt_size_dist(res=res,yolo_root=yolo_root, format=format,s=s, box_format=box_format)
    else:
        _, _, hw_pair = cal_tgt_size_dist(coco_root=coco_root, format=format,s=s, box_format=box_format)
    # hw_pair = hw_pair[:100]
    h_threshold = 100
    w_threshold = 100
    if isinstance(threshold, (list, tuple)):
        h_threshold = threshold[0]
        w_threshold = threshold[1]
    elif isinstance(threshold, (int, float)):
        h_threshold = threshold
        w_threshold = threshold
    hs = []
    ws = []
    if base is not None:
        for i in range(len(hw_pair)):
            x = hw_pair[i][0] // base * base
            y = hw_pair[i][1] // base * base
            hw_pair[i] = (x, y)
    fig = plt.figure()
    counter = dict(Counter(hw_pair))
    for k, v in counter.items():

        if threshold is not None and k[0] > h_threshold or k[1] > w_threshold:
            continue
        hs.append(k[0])
        ws.append(k[1])
    heat_map_data = []
    max_w = max(ws)
    max_h = max(hs)
    for i in range(max_h):
        heat_map_data.append([])
        for j in range(max_w):
            if (i, j) in counter:
                heat_map_data[i].append(counter[(i, j)])
            else:
                heat_map_data[i].append(0)
    heat_map_data = pd.DataFrame(heat_map_data)
    sb.heatmap(heat_map_data)
    plt.xlabel('height')
    plt.ylabel('width')
    plt.savefig(filename)
