# -*- encoding: utf-8 -*-
"""
@Time: 2024-03-11 18:46
@Auth: xjjxhxgg
@File: setup.py
@IDE: PyCharm
@Motto: xhxgg
"""
from setuptools import setup, find_packages

setup(
    name='pyzyj',
    version='1.1.9',
    author='zyj',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'numpy',
        'Pillow',
        'pycocotools',
        'lxml',
        # 'torch',
        # 'torchvision',
        'tqdm',
        'matplotlib',
        'scikit-image',
        'scikit-learn',
        'pandas',
        'pyyaml',
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ZYJIQVV/pyzyj',
    license='MIT',
)
