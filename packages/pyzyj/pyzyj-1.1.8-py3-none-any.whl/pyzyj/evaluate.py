import os
import numpy as np
import torch
from tqdm import tqdm
from pathlib import Path
from matplotlib import pyplot as plt
import warnings
from ultralytics.utils import LOGGER, SimpleClass, TryExcept, plt_settings
from ultralytics.utils.metrics import box_iou, SimpleClass, Metric, DetMetrics, smooth, compute_ap, ap_per_class
device = torch.device(0)

def load_yolo_labels(file_path):
    with open(file_path, 'r') as f:
        labels = [[float(i) for i in line.strip().split()] for line in f.readlines()]
    labels = [(label[0], label[1] - label[3] / 2, label[2] - label[4] / 2, label[1] + label[3] / 2, label[2] + label[4] / 2) for label in labels]
    labels = np.array([(int(label[0]), float(label[1]), float(label[2]), float(label[3]), float(label[4])) for label in labels])
    cls = labels[:, 0]
    bbox = labels[:, 1:]
    return labels, cls, bbox
def load_prd_with_conf(file_path):
    with open(file_path, 'r') as f:
        labels = [[float(i) for i in line.strip().split()] for line in f.readlines()]
    try:
        labels = [(label[0], label[1] - label[3] / 2, label[2] - label[4] / 2, label[1] + label[3] / 2, label[2] + label[4] / 2, label[5]) for label in labels]
    except:
        labels = [(label[0], label[1] - label[3] / 2, label[2] - label[4] / 2, label[1] + label[3] / 2, label[2] + label[4] / 2, 1) for label in labels]
    labels = np.array([(int(label[0]), float(label[1]), float(label[2]), float(label[3]), float(label[4]), float(label[5])) for label in labels])
    cls = labels[:, 0]
    bbox = labels[:, 1:5]
    conf = labels[:, 5]
    return labels, cls, bbox, conf


def calculate_tps(all_ground_truths, all_detections, thrhds=None):
    if thrhds is None:
        thrhds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    tps = []
    for thrhd in tqdm(thrhds):
        tps.append(calculate_tp(all_ground_truths, all_detections, thrhd))
    return np.array(tps).transpose(1, 0)

def calculate_tp(all_ground_truths, all_detections, thrhd):
    TP_for_each_file = []
    for ground_truths, detections in zip(all_ground_truths, all_detections):
        matched = set()
        TP = []
        for det in detections:
            found_match = False
            for idx, gt in enumerate(ground_truths):
                if idx in matched:
                    continue
                if det[0] == gt[0]: # class matched
                    if box_iou(torch.tensor(gt[None, 1:], device=device), torch.tensor(det[None, 1:], device=device)) >= thrhd:
                        TP.append(True)
                        TP_for_each_file.append(True)
                        matched.add(idx)
                        found_match = True
                        break
            if not found_match:
                TP.append(False)
                TP_for_each_file.append(False)

    return np.array(TP_for_each_file)

if __name__ == '__main__':
    # names = {0:'ship', 1:'plane', 2:'vehicle'}
    names = {i:str(i) for i in range(80)}
    lbl_rt = r'F:\611\coco128\labels\train2017'
    prd_rt = r'F:\611\coco128\preds'

    lbl_files = [os.path.join(lbl_rt, lbl) for lbl in os.listdir(lbl_rt)]
    prd_files = [os.path.join(prd_rt, lbl) for lbl in os.listdir(prd_rt)]

    lbl_files = [fr'{lbl_rt}\000000000357.txt', fr'{lbl_rt}\000000000472.txt']
    # prd_files = [fr'{lbl_rt}\000000000357.txt', fr'{lbl_rt}\000000000472.txt']
    prd_files = [fr'{prd_rt}\000000000357.txt', fr'{prd_rt}\000000000472.txt']
    metrics = Metric()

    detections_for_each_file = []
    gt_cls_for_each_file = np.array([])
    gt_box_for_each_file = []

    for lbl_file in tqdm(lbl_files):
        lbls, gt_cls, gt_box = load_yolo_labels(lbl_file)
        detections_for_each_file.append(lbls)
        gt_cls_for_each_file = np.append(gt_cls_for_each_file, gt_cls)
        gt_box_for_each_file.append(gt_box)

    predictions_for_each_file = []
    pd_cls_for_each_file = np.array([])
    pd_box_for_each_file = np.array([])
    pd_conf_for_each_file = np.array([])

    for prd_file in tqdm(prd_files):
        prds, pd_cls, pd_box, conf = load_prd_with_conf(prd_file)
        predictions_for_each_file.append(prds[:, :-1])
        pd_cls_for_each_file = np.append(pd_cls_for_each_file, pd_cls)
        pd_box_for_each_file = np.append(pd_box_for_each_file, pd_box)
        pd_conf_for_each_file = np.append(pd_conf_for_each_file, conf)
    pd_conf_for_each_file = np.array(pd_conf_for_each_file).reshape(-1)
    gt_cls_for_each_file = np.array(gt_cls_for_each_file).reshape(-1)
    pd_cls_for_each_file = np.array(pd_cls_for_each_file).reshape(-1)

    TP_for_each_file = calculate_tps(detections_for_each_file, predictions_for_each_file)
    res = ap_per_class(TP_for_each_file, pd_conf_for_each_file, pd_cls_for_each_file,gt_cls_for_each_file, names=names)
    tp, fp, p, r, f1, ap, unique_classes, p_curve, r_curve, f1_curve, x, prec_values = res

    metrics.update(res[2:])
    print(res)


