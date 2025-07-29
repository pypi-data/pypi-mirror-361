from ultralytics import YOLO

if __name__ == '__main__':
    yolo = YOLO('yolov8n.pt')
    # data = 'data.yaml'
    data = 'coco128.yaml'
    yolo.val(data=data, device='cpu', batch=5)