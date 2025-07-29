# -*- coding: utf-8 -*-
"""
@Time: 2024-01-29 13:30
@Auth: xjjxhxgg
@File: visualize.py
@IDE: PyCharm
@Motto: xhxgg
"""
from typing import Union

import cv2
import os
import json
import numpy as np
from .format import xml_parser, yolo_parser
from pycocotools.coco import COCO


def visualize_one(img_path: str, ann_path: str, save_path: str = None, color: tuple = None, parser: callable = None,
                  format: str = 'yolo', cats=None) -> None:
    """
    visualize the image with annotations, at present only support object detection with bbox
    :param img_path: the path of image
    :param ann_path: the path of annotation file
    :param save_path: if not None, save the image with bbox to save_path else show the image with bbox
    :param color: the color of bbox or mask
    :param parser: if ann_path is xml, parser is required, which is a callable function and returns a list of bbox
     like [{'name':name, 'bbox':[xmin,ymin,xmax,ymax]},...] or [[xmin,ymin,xmax,ymax],...].
     It takes ann_path as input if the annotations for each image are in a seperate file respectively.,
     or takes img_path and ann_path as input if the annotations for each image are all in one file,
     and the parser should accept img_path as the first input and ann_path the second.
     A simple parser is provided in format.py
    :param format: the format of annotation file which should be in ['custom', 'yolo'].
     If format is 'custom', a  parser is needed which returns the same format as above.
    :return:
    """
    img = None
    if color is None:
        color = (0, 0, 255)
    if ann_path.endswith('.json'):
        if parser is None:  # coco
            filename = os.path.basename(img_path)
            coco = COCO(ann_path)
            imgs = coco.imgs
            img_id = None
            file_name_key = 'file_name' if 'file_name' in imgs[coco.getImgIds()[0]] else 'filename'
            for img in imgs.values():
                if img[file_name_key] == filename:
                    img_id = img['id']
                    break
            img = cv2.imread(img_path)
            if img_id is None:
                raise Exception('Image not found in ann file')
            anns = coco.loadAnns(coco.getAnnIds(imgIds=img_id))  # coco.loadAnns(4635)
            if len(anns) == 0:
                raise Exception('No bbox found in ann file')
            for ann_ann in anns:
                bbox = ann_ann['bbox']
                xmin = (bbox[0])
                ymin = bbox[1]
                w = bbox[2]
                h = bbox[3]
                xmax = xmin + w
                ymax = ymin + h
                xmin = int(xmin)
                ymin = int(ymin)
                xmax = int(xmax)
                ymax = int(ymax)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
        else:
            bboxes = parser(img_path, ann_path)
            img = cv2.imread(img_path)
            if len(bboxes) == 0:
                raise Exception('No bbox found in ann file')
            for bbox in bboxes:
                if isinstance(bbox, dict):
                    bbox = bbox['bbox']
                x = bbox[0]
                y = bbox[1]
                w = bbox[2]
                h = bbox[3]

                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    elif ann_path.endswith('.xml'):  # voc
        if parser is None:
            raise Exception('parser is None')
        img = cv2.imread(img_path)
        bboxes = parser(ann_path)
        if len(bboxes) == 0:
            raise Exception('No bbox found in ann file')
        for bbox in bboxes:
            if isinstance(bbox, dict):
                bbox = bbox['bbox']
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    elif ann_path.endswith('.txt'):
        if format == 'yolo':  # yolo
            img = cv2.imread(img_path)
            img_h, img_w, _ = img.shape
            bboxes = yolo_parser(ann_path, img_w, img_h)
            if len(bboxes) == 0:
                raise Exception('No bbox found in ann file')
            for bbox in bboxes:
                name = bbox['name']
                bbox = bbox['bbox']
                xmin, ymin, xmax, ymax = bbox
                name = str(name) if cats is None else cats[name]
                cv2.putText(img, name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)

        elif format == 'custom':
            if parser is None:
                raise Exception('parser is None')
            img = cv2.imread(img_path)
            bboxes = parser(ann_path)
            if len(bboxes) == 0:
                raise Exception('No bbox found in ann file')
            for bbox in bboxes:
                if isinstance(bbox, dict):
                    bbox = bbox['bbox']
                x = bbox[0]
                y = bbox[1]
                w = bbox[2]
                h = bbox[3]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    else:
        raise Exception('Annotation file not supported: {}'.format(ann_path))
    if img is not None:
        if save_path is not None:
            if os.path.isdir(save_path):
                save_path = os.path.join(save_path, 'vis.jpg')
            cv2.imwrite(save_path, img)
        else:
            cv2.imshow('vis', img)
            cv2.waitKey(0)
    else:
        raise Exception('Image not found')


def visualize(img_path: str, ann_path: str, save_path: str = None, color: tuple = None, parser: callable = None,
              format: str = 'yolo', cats=None) -> None:
    if not os.path.isdir(img_path):
        visualize_one(img_path, ann_path, save_path, color, parser, format, cats=cats)
    else:
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        for root, dirs, files in os.walk(img_path):
            for file in files:
                img = os.path.join(root, file)
                ann = os.path.join(ann_path, os.path.splitext(file)[0] + '.txt')
                sv_path = fr'{save_path}/{file}' if save_path is not None else None
                visualize_one(img, ann, sv_path, color, parser, format, cats=cats)




def draw_obb(image, obb_points, color=(0, 255, 0), thickness=2):
    """
    Draw oriented bounding box (OBB) on the image.

    Parameters:
        image (numpy.ndarray): Input image.
        obb_points (list): List of eight coordinates representing the OBB box.
        color (tuple): Color of the OBB box in BGR format.
        thickness (int): Thickness of the lines used to draw the OBB box.

    Returns:
        numpy.ndarray: Image with the OBB box drawn.
    """
    obb_points = np.array(obb_points, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(image, [obb_points], isClosed=True, color=color, thickness=thickness)
    return image


