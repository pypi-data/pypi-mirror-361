# -*- coding: utf-8 -*-
"""
@Time: 2024-01-23 20:30
@Auth: xjjxhxgg
@File: __init__.py
@IDE: PyCharm
@Motto: xhxgg
"""
from .format import (
    coco2yolo, yolo2coco, xml2yolo, yolo2coco_n,
    yolo_parser, yolo_obb_parser, coco_parser, xml_parser, xml_parser_obb,
    tif2jpg,
)
from .visualize import visualize

compenents = {
    'coco2yolo': coco2yolo,
    'yolo2coco': yolo2coco,
    'xml2yolo': xml2yolo,
    'yolo2coco_n': yolo2coco_n,
    'yolo_parser': yolo_parser,
    'yolo_obb_parser': yolo_obb_parser,
    'coco_parser': coco_parser,
    'xml_parser': xml_parser,
    'xml_parser_obb': xml_parser_obb,
    'tif2jpg': tif2jpg,
    'visualize': visualize
}
