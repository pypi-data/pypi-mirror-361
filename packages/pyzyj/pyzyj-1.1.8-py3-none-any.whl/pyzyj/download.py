# -*- coding: utf-8 -*-
"""
@Time: 2024-02-03 17:55
@Auth: xjjxhxgg
@File: download.py
@IDE: PyCharm
@Motto: xhxgg
"""
import requests


def get(url, file, mode='wb'):
    """
    Given a URL, this function will download the content and save it to the specified location as the specified format.
    :param url: the URL of the content to be downloaded
    :param file: the location where the content will be saved, including the file name and extension name
    :param mode: the format of the content to be saved, 'wb' for binary file and 'w' for text file
    :return: None
    """
    response = requests.get(url)
    if mode == 'wb':
        with open(file, mode) as f:
            f.write(response.content)
    else:
        with open(file, mode, encoding='utf-8') as f:
            f.write(response.text)
