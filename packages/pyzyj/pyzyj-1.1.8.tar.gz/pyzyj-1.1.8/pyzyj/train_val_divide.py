# -*- coding: utf-8 -*-
"""
@Time: 2024-01-29 14:45
@Auth: xjjxhxgg
@File: train_val_divide.py
@IDE: PyCharm
@Motto: xhxgg
"""
import random
import json
import copy


def coco_divide(coco_json, train_json, val_json, train_ratio=0.8):
    import json
    import random
    coco_json = json.load(open(coco_json, 'r'))
    images = coco_json['images']
    annotations = coco_json['annotations']
    categories = coco_json['categories']
    train_images = []
    val_images = []
    train_annotations = []
    val_annotations = []
    train_categories = []
    val_categories = []
    train_img_ids = []
    val_img_ids = []
    for img in images:
        if random.random() < train_ratio:
            train_images.append(img)
            train_img_ids.append(img['id'])
        else:
            val_images.append(img)
            val_img_ids.append(img['id'])
    for ann in annotations:
        if ann['image_id'] in train_img_ids:
            train_annotations.append(ann)
        else:
            val_annotations.append(ann)
    for cat in categories:
        if cat['id'] in [ann['category_id'] for ann in train_annotations]:
            train_categories.append(cat)
        else:
            val_categories.append(cat)
    train = {
        'images': train_images,
        'annotations': train_annotations,
        'categories': train_categories,
        'info': [],
        'license': []
    }
    val = {
        'images': val_images,
        'annotations': val_annotations,
        'categories': val_categories,
        'info': [],
        'license': []
    }
    json.dump(train, open(train_json, 'w'))
    json.dump(val, open(val_json, 'w'))


def yolo_divide(total_lbl_root, total_img_root, yolo_root, train_ratio=0.8):
    import os
    import shutil
    for root, dirs, files in os.walk(total_lbl_root):
        for file in files:
            if file.endswith('.txt'):
                if random.random() < train_ratio:
                    shutil.copy(str(os.path.join(total_lbl_root, file)),
                                str(os.path.join(yolo_root, 'labels', 'train', file)))
                    shutil.copy(str(os.path.join(total_img_root, file.replace('.txt', '.jpg'))),
                                str(os.path.join(yolo_root, 'images', 'train', file.replace('.txt', '.jpg'))))
                else:
                    shutil.copy(str(os.path.join(total_lbl_root, file)),
                                str(os.path.join(yolo_root, 'labels', 'val', file)))
                    shutil.copy(str(os.path.join(total_img_root, file.replace('.txt', '.jpg'))),
                                str(os.path.join(yolo_root, 'images', 'val', file.replace('.txt', '.jpg'))))


def coco_merge(*args):
    """
    Merge multiple coco json files into one. All the json files should have the totally same categories.
    :param args:
    :return:
    """
    coco_json1 = args[0]
    coco_json2 = args[1]
    json_cnt = 2
    json1 = json.load(open(coco_json1, 'r'))
    json2 = json.load(open(coco_json2, 'r'))
    img_id = 0
    ann_id = 0
    merged_json, img_id, ann_id = __merge(json1, json2, img_id, ann_id)
    while json_cnt < len(args):
        new_json = json.load(open(args[json_cnt], 'r'))
        merged_json, img_id, ann_id = __merge(merged_json, new_json, img_id, ann_id)
        json_cnt += 1
    return merged_json


def __merge(json1, json2, img_id, ann_id):
    merged_json = {'images': [], 'annotations': [], 'categories': copy.deepcopy(json1['categories']),
                   'linceses': copy.deepcopy(json1['linceses']), 'info': copy.deepcopy(json1['info'])}
    images1 = json1['images']
    images2 = json2['images']
    annotations1 = json1['annotations']
    annotations2 = json2['annotations']
    img_id_map = {1: {}, 2: {}}
    ann_id_map = {1: {}, 2: {}}
    for img in images1:
        img_id = max(img_id, img['id'])
    img_id += 1
    for ann in annotations1:
        ann_id = max(ann_id, ann['id'])
    ann_id += 1
    for img in images1:
        new_img = img.copy()
        new_img['id'] = img_id
        img_id_map[1][img['id']] = img_id
        img_id += 1
        merged_json['images'].append(new_img)
    for img in images2:
        new_img = img.copy()
        new_img['id'] = img_id
        img_id_map[2][img['id']] = img_id
        img_id += 1
        merged_json['images'].append(new_img)
    for ann in annotations1:
        new_ann = ann.copy()
        new_ann['id'] = ann_id
        new_ann['image_id'] = img_id_map[1][ann['image_id']]
        ann_id_map[1][ann['id']] = ann_id
        ann_id += 1
        merged_json['annotations'].append(new_ann)
    for ann in annotations2:
        new_ann = ann.copy()
        new_ann['id'] = ann_id
        new_ann['image_id'] = img_id_map[2][ann['image_id']]
        ann_id_map[2][ann['id']] = ann_id
        ann_id += 1
        merged_json['annotations'].append(new_ann)

    return merged_json, img_id, ann_id
