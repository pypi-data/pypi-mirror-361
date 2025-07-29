import torch

def model_parameters(model):
    return sum(p.numel() for p in model.parameters())

