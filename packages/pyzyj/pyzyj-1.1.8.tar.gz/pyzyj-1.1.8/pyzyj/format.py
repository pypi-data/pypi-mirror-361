# -*- coding: utf-8 -*-
"""
@Time: 2024-01-23 20:20
@Auth: xjjxhxgg
@File: coco_to_yolo.py
@IDE: PyCharm
@Motto: xhxgg
"""

import json
import math
import os

import cv2


def coco2yolo(json_path, yolo_root, cat_reid=False):
    ann_file = json.load(open(json_path, 'r'))
    images = ann_file['images']
    annotations = ann_file['annotations']
    categories = ann_file['categories']
    categories_reid = [cat['id'] for cat in categories]
    categories_reid.sort()
    img_ann_map = {}
    for img in images:
        img_ann_map[img['id']] = []
    for ann in annotations:
        img_ann_map[ann['image_id']].append(ann)
    file_name_key = 'file_name' if 'file_name' in images[0] else 'filename'
    for img in images:
        img_name = img[file_name_key]
        img_width = img['width']
        img_height = img['height']
        img_id = img['id']
        img_anns = img_ann_map[img_id]
        yolo_txt_path = os.path.join(yolo_root, img_name.split('.')[0] + '.txt')
        with open(yolo_txt_path, 'w') as f:
            for ann in img_anns:
                cat_id = ann['category_id']
                if cat_reid:
                    cat_id = categories_reid.index(cat_id)
                bbox = ann['bbox']
                x = bbox[0]
                y = bbox[1]
                w = bbox[2]
                h = bbox[3]
                x_center = x + w / 2
                y_center = y + h / 2
                x_center /= img_width
                y_center /= img_height
                w /= img_width
                h /= img_height
                f.write(str(cat_id) + ' ' + str(x_center) + ' ' + str(y_center) + ' ' + str(w) + ' ' + str(h) + '\n')
    # write the name_catid to a file
    with open(os.path.join(yolo_root, 'name_catid.txt'), 'w') as f:
        if cat_reid:
            # replace the cat_id with the reid
            for cat in categories:
                cat['id'] = categories_reid.index(cat['id'])
        for name, cat in categories.items():
            f.write(name + ' ' + str(cat) + '\n')

def yolo2coco(yolo_root, json_path, categories, img_root, img_id=0, ann_id=0, info='', licenses='', img_suffix='.jpg'):
    ann_file = open(json_path, 'w')
    images = []
    annotations = []
    for root, dirs, files in os.walk(yolo_root):
        for file in files:
            if file.endswith('.txt'):
                img_id += 1
                img_name = file.split('.')[0] + img_suffix
                img_file = fr'{img_root}\{img_name}'
                img = cv2.imread(img_file)
                height, width, _ = img.shape
                img = {'file_name': img_name, 'height': height, 'width': width, 'id': img_id}
                images.append(img)
                txt_path = os.path.join(root, file)
                with open(txt_path, 'r') as f:
                    for line in f.readlines():
                        line = line.strip()
                        if line == '':
                            continue
                        cat, x, y, w, h = line.split(' ')
                        x = float(x)
                        y = float(y)
                        w = float(w)
                        h = float(h)
                        x *= width
                        y *= height
                        w *= width
                        h *= height
                        xmin = int(x - w / 2)
                        ymin = int(y - h / 2)
                        cat = int(cat)
                        bbox = [xmin, ymin, w, h]
                        ann_id += 1
                        ann = {'id': ann_id, 'image_id': img_id, 'category_id': cat, 'bbox': bbox, 'area': w * h, 'iscrowd': 0}
                        annotations.append(ann)
    ann_file.write(json.dumps(
        {'images': images, 'annotations': annotations, 'categories': categories, 'info': info, 'licenses': licenses}))
    ann_file.close()

def yolo2coco_n(yolo_root, json_path, categories, n, img_id=0, ann_id=0, info='', licenses=''):
    """

    :param yolo_root:
    :param json_path:
    :param categories:
    :param n: train, val or test to specify which sub-dataset to transfer
    :param img_id:
    :param ann_id:
    :param info:
    :param licenses:
    :return:
    """
    # img_root = os.path.join(yolo_root, 'images', n)
    img_root = fr'{yolo_root}\images\{n}'
    # lbl_root = os.path.join(yolo_root, 'labels', n)
    lbl_root = fr'{yolo_root}\labels\{n}'
    files = os.listdir(lbl_root)
    ann_file = open(json_path, 'w')
    images = []
    annotations = []
    for file in files:
        if file.endswith('.txt'):
            img_id += 1
            img_name = file.split('.')[0] + '.jpg'
            img_file = os.path.join(img_root, img_name)
            img = cv2.imread(img_file)
            height, width, _ = img.shape
            img = {'file_name': img_name, 'height': height, 'width': width, 'id': img_id}
            images.append(img)
            txt_path = os.path.join(lbl_root, file)
            with open(txt_path, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == '':
                        continue
                    cat, x, y, w, h = line.split(' ')
                    x = float(x)
                    y = float(y)
                    w = float(w)
                    h = float(h)
                    x *= width
                    y *= height
                    w *= width
                    h *= height
                    xmin = int(x - w / 2)
                    ymin = int(y - h / 2)
                    cat = int(cat)
                    bbox = [xmin, ymin, w, h]
                    ann_id += 1
                    ann = {'id': ann_id, 'image_id': img_id, 'category_id': cat, 'bbox': bbox, 'area': h * w, 'iscrowd': 0}
                    annotations.append(ann)
    ann_file.write(json.dumps(
        {'images': images, 'annotations': annotations, 'categories': categories, 'info': info, 'licenses': licenses}))
    ann_file.close()

def coco_parser(ann_path):
    '''
    return {'images': images, 'categories': categories, 'img_ann_map': img_ann_map}
    :param ann_path:
    :return:
    '''
    ann = json.load(open(ann_path, 'r'))
    images = ann['images']
    annotations = ann['annotations']
    categories = ann['categories']
    img_ann_map = {}
    for img in images:
        img_id = img['id']
        img_ann_map[img_id] = []
        for ann in annotations:
            if ann['image_id'] == img_id:
                img_ann_map[img_id].append(ann)

    return {'images': images, 'categories': categories, 'img_ann_map': img_ann_map}


def yolo_parser(yolo_path, img_w=None, img_h=None):
    """
    return bboxes [{'name':name,'bbox':[xmin,ymin,xmax,ymax]},...] or [{'name':name,'bbox':[cx,cy,w,h]},...]
    :param yolo_path:
    :param img_w: image width
    :param img_h: image height
    if img_w and img_h are not None, the bbox will be scaled to the original image size,
    otherwise the bbox is the relative size
    :return:
    """
    bboxes = []
    with open(yolo_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            cat, x, y, w, h = line.split(' ')
            cat = int(cat)
            cx = float(x)
            cy = float(y)
            w = float(w)
            h = float(h)
            if img_w and img_h:
                xmin = int((cx - w / 2) * img_w)
                ymin = int((cy - h / 2) * img_h)
                xmax = int((cx + w / 2) * img_w)
                ymax = int((cy + h / 2) * img_h)
                bboxes.append({'name': cat, 'bbox': [xmin, ymin, xmax, ymax]})
            else:
                bboxes.append({'name': cat, 'bbox': [cx, cy, w, h]})
    return bboxes

def yolo_obb_parser(yolo_path, img_w=None, img_h=None):
    """
    return bboxes [{'name':name,'bbox':[xmin,ymin,xmax,ymax]},...] or [{'name':name,'bbox':[cx,cy,w,h]},...]
    :param yolo_path:
    :param img_w: image width
    :param img_h: image height
    if img_w and img_h are not None, the bbox will be scaled to the original image size,
    otherwise the bbox is the relative size
    :return:
    """
    bboxes = []
    with open(yolo_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            cat, xlt, ylt, xrt, yrt, xrb, yrb, xlb, ylb = line.split(' ')
            cat = int(cat)
            xlt = float(xlt)
            ylt = float(ylt)
            xrt = float(xrt)
            yrt = float(yrt)
            xrb = float(xrb)
            yrb = float(yrb)
            xlb = float(xlb)
            ylb = float(ylb)
            obbw = math.sqrt((xlt - xrt) ** 2 + (ylt - yrt) ** 2)
            obbh = math.sqrt((xlt - xlb) ** 2 + (ylt - ylb) ** 2)
            # calculate the minimum bounding rectangle
            brw = max(xlt, xrt, xrb, xlb) - min(xlt, xrt, xrb, xlb)
            brh = max(ylt, yrt, yrb, ylb) - min(ylt, yrt, yrb, ylb)
            brcx = (xlt + xrt + xrb + xlb) / 4
            brcy = (ylt + yrt + yrb + ylb) / 4
            if img_w and img_h:
                brxmin = int((brcx - brw / 2) * img_w)
                brymin = int((brcy - brh / 2) * img_h)
                brxmax = int((brcx + brw / 2) * img_w)
                brymax = int((brcy + brh / 2) * img_h)
                xlt = int(xlt * img_w)
                ylt = int(ylt * img_h)
                xrt = int(xrt * img_w)
                yrt = int(yrt * img_h)
                xrb = int(xrb * img_w)
                yrb = int(yrb * img_h)
                xlb = int(xlb * img_w)
                ylb = int(ylb * img_h)
                obbw = int(obbw * img_w)
                obbh = int(obbh * img_h)
                bboxes.append({'name': cat, 'br': [brxmin, brymin, brxmax, brymax], 'bbox': [xlt, ylt, xrt, yrt, xrb, yrb, xlb, ylb, obbw, obbh]})
            else:
                bboxes.append({'name': cat, 'br': [brcx, brcy, brw, brh], 'bbox': [xlt, ylt, xrt, yrt, xrb, yrb, xlb, ylb, obbw, obbh]})

    return bboxes


def xml_parser(ann_path):
    '''
    return bboxes [{'name':name,'bbox':[xmin,ymin,xmax,ymax]},...]
    :param ann_path:
    :return:
    '''
    from xml.dom import minidom
    tree = minidom.parse(ann_path)
    root = tree.documentElement
    objects = root.getElementsByTagName('object')
    bboxes = []
    size = root.getElementsByTagName('size')
    H = size.getElementsByTagName('height')[0].data
    W = size.getElementsByTagName('width')[0].data
    H = float(H)
    W = float(W)
    for object in objects:
        name = object.getElementsByTagName('name')[0].childNodes[0].data
        bndboxes = object.getElementsByTagName('bndbox')
        for bndbox in bndboxes:
            xmin = int(bndbox.getElementsByTagName('xmin')[0].childNodes[0].data)
            ymin = int(bndbox.getElementsByTagName('ymin')[0].childNodes[0].data)
            xmax = int(bndbox.getElementsByTagName('xmax')[0].childNodes[0].data)
            ymax = int(bndbox.getElementsByTagName('ymax')[0].childNodes[0].data)
            bboxes.append({'name': name, 'bbox': [xmin, ymin, xmax, ymax]})
    return bboxes, H, W

def xml_parser_obb(ann_path):
    '''
    return bboxes [{'name':name,'bbox':[tlx, tly, trx, try, brx, bry, blx, bly, obbw, obbh]},...]
    :param ann_path:
    :return:
    '''
    from xml.dom import minidom
    tree = minidom.parse(ann_path)
    root = tree.documentElement
    objects = root.getElementsByTagName('object')
    bboxes = []
    witdh = int(root.getElementsByTagName('width')[0].childNodes[0].data)
    height = int(root.getElementsByTagName('height')[0].childNodes[0].data)
    for object in objects:
        name = object.getElementsByTagName('name')[0].childNodes[0].data
        points = object.getElementsByTagName('points')
        for point in points:
            tlx = float(point.getElementsByTagName('point')[1].childNodes[0].data.split(',')[0])
            tly = float(point.getElementsByTagName('point')[1].childNodes[0].data.split(',')[1])
            trx = float(point.getElementsByTagName('point')[2].childNodes[0].data.split(',')[0])
            try_ = float(point.getElementsByTagName('point')[2].childNodes[0].data.split(',')[1])
            brx = float(point.getElementsByTagName('point')[3].childNodes[0].data.split(',')[0])
            bry = float(point.getElementsByTagName('point')[3].childNodes[0].data.split(',')[1])
            blx = float(point.getElementsByTagName('point')[4].childNodes[0].data.split(',')[0])
            bly = float(point.getElementsByTagName('point')[4].childNodes[0].data.split(',')[1])
            obbw = math.sqrt((tlx - trx) ** 2 + (tly - try_) ** 2)
            obbh = math.sqrt((tlx - blx) ** 2 + (tly - bly) ** 2)
            tlx /= witdh
            tly /= height
            trx /= witdh
            try_ /= height
            brx /= witdh
            bry /= height
            blx /= witdh
            bly /= height
            bboxes.append({'name': name, 'bbox': [tlx, tly, trx, try_, brx, bry, blx, bly, obbw, obbh]})
    return bboxes

def xml2yolo(xml_root, yolo_root, xml_parser=xml_parser, name_catid=None):
    """
    convert the xml annotation to yolo format
    :param xml_root:
    :param yolo_root:
    :return:
    """
    if name_catid is None:
        name_catid = {}
    for root, dirs, files in os.walk(xml_root):
        for file in files:
            if file.endswith('.xml'):
                xml_path = os.path.join(root, file)
                bboxes, H, W = xml_parser(xml_path)
                with open(os.path.join(yolo_root, 'labels', file.split('.')[0] + '.txt'), 'w') as f:
                    for bbox in bboxes:
                        name = bbox['name']
                        if name not in name_catid:
                            name_catid[name] = len(name_catid)
                        cat = name_catid[name]
                        bbox = bbox['bbox']
                        if len(bbox) > 4:
                            raise 'Invalid bbox format'
                        bbox[0] = bbox[0] / W
                        bbox[1] = bbox[1] / H
                        bbox[2] = bbox[2] / W
                        bbox[3] = bbox[3] / H
                        w = bbox[2] - bbox[0]
                        h = bbox[3] - bbox[1]
                        bbox[0] = bbox[0] + w / 2
                        bbox[1] = bbox[1] + h / 2
                        bbox[2] = w
                        bbox[3] = h
                        bbox = ' '.join([str(b) for b in bbox])
                        bbox = ' '.join([str(b) for b in bbox])
                        f.write(str(cat) + ' ' + bbox + '\n')
    # write the name_catid to a file
    with open(os.path.join(yolo_root, 'name_catid.txt'), 'w') as f:
        for name, cat in name_catid.items():
            f.write(name + ' ' + str(cat) + '\n')

def xml2yolo_obb(xml_root, yolo_root, xml_parser=xml_parser_obb,name_catid=None):
    """
    convert the xml annotation to yolo format
    :param xml_root:
    :param yolo_root:
    :return:
    """
    if name_catid is None:
        name_catid = {}
    for root, dirs, files in os.walk(xml_root):
        for file in files:
            if file.endswith('.xml'):
                xml_path = os.path.join(root, file)
                obbs = xml_parser(xml_path)
                with open(os.path.join(yolo_root, 'labels', file.split('.')[0] + '.txt'), 'w') as f:
                    for obb in obbs:
                        name = obb['name']
                        if name not in name_catid:
                            name_catid[name] = len(name_catid)
                        cat = name_catid[name]
                        bbox = obb['bbox']
                        if len(bbox) > 8:
                            bbox = bbox[:8]
                        bbox = ' '.join([str(b) for b in bbox])
                        f.write(str(cat) + ' ' + bbox + '\n')
    # write the name_catid to a file
    with open(os.path.join(yolo_root, 'name_catid.txt'), 'w') as f:
        for name, cat in name_catid.items():
            f.write(name + ' ' + str(cat) + '\n')



def tif2jpg(tif_root, jpg_root):
    from PIL import Image
    for root, dirs, files in os.walk(tif_root):
        for file in files:
            if file.endswith('.tif'):
                tif_path = os.path.join(root, file)
                img = Image.open(tif_path)
                img = img.convert('RGB')
                img.save(os.path.join(jpg_root, file.split('.')[0] + '.jpg'))

