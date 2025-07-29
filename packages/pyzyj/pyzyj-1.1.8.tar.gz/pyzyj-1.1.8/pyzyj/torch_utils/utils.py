# -*- encoding: utf-8 -*-
"""
@Time: 2025/7/9 19:15
@Auth: xjjxhxgg
@File: utils.py
@IDE: PyCharm
@Project: pyzyj
@Motto: xhxgg
"""
import torch

def compare_models(model1, model2, state_dict_map=None):
    """
    Compare two PyTorch models for equality.

    Args:
        model1 (torch.nn.Module): First model to compare.
        model2 (torch.nn.Module): Second model to compare.
        state_dict_map (dict, optional): A mapping that maps state_dict keys from model1 to model2.
            If provided, it will be used to compare the mapped keys instead of the original keys.

    Returns:
        bool: True if models are equal, False otherwise.
    """
    sd1 = model1.state_dict()
    sd2 = model2.state_dict()

    if state_dict_map is None:
        state_dict_map = {key: key for key in sd1.keys()}
    elif sd1.keys() != sd2.keys():
        return False

    for key in sd1.keys():
        if not torch.equal(sd1[key], sd2[state_dict_map[key]]):
            return False
    return True
