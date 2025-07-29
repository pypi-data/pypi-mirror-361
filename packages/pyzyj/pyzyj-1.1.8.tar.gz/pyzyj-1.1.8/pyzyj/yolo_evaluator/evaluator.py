from ultralytics import YOLO

class YOLOEvaluator:
    def __init__(self, data, device):
        self.model = YOLO('yolov8n.yaml')
        self.data = data
        self.device = device
    def __call__(self, *args, **kwargs):
        self.model.val(data=self.data, device=self.device)