import os
import shutil

def select_images_by_names(img_dir, names, save_dir, suffix='.jpg'):
    """
    Select images by names
    :param img_dir: the directory of images
    :param names: the names of images to be selected. A list of strings or a string indicating the .txt file containing the names
    :param save_dir: the directory to save the selected images
    :return: None
    """
    if isinstance(names, str):
        with open(names, 'r') as f:
            names = f.readlines()
            names = [name.strip() for name in names]
        if len(names) == 0:
            raise f'{names} is empty'
    # check if the names are with extension
    l = os.path.splitext(names[0])
    if l[1] == '':
        names = [name + suffix for name in names]

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for name in names:
        img_path = fr'{img_dir}\{name}'
        if os.path.exists(img_path):
            save_path = fr'{save_dir}\{name}'
            shutil.copy(img_path, save_path)
        else:
            print(f'{img_path} does not exist')


def select_yolo_labels_by_names(lbl_dir, names, save_dir, suffix='.txt'):
    """
    Select yolo labels by names
    :param lbl_dir: the directory of yolo labels
    :param names: the names of yolo labels to be selected. A list of strings or a string indicating the .txt file containing the names
    :param save_dir: the directory to save the selected yolo labels
    :return: None
    """
    if isinstance(names, str):
        with open(names, 'r') as f:
            names = f.readlines()
            names = [name.strip() for name in names]
        if len(names) == 0:
            raise f'{names} is empty'
    # check if the names are with extension
    l = os.path.splitext(names[0])
    if l[1] == '':
        names = [name + suffix for name in names]

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for name in names:
        lbl_path = fr'{lbl_dir}\{name}'
        if os.path.exists(lbl_path):
            save_path = fr'{save_dir}\{name}'
            shutil.copy(lbl_path, save_path)
        else:
            print(f'{lbl_path} does not exist')

