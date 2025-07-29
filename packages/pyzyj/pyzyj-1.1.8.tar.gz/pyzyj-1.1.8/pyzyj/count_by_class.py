import os
from collections import Counter
from tqdm import tqdm

nc = 80
cats = {i:str(i) for i in range(nc)}
clses = []
lbl_rt = r'F:\TempFiles\ForPyCharm\pythonProject\coco128\labels\train2017'
lbls = os.listdir(lbl_rt)
for lbl in tqdm(lbls):
    lbl_f = fr'{lbl_rt}\{lbl}'
    with open(lbl_f, 'r', encoding='utf8') as f:
        lines = f.readlines()
    for line in lines:
        if not line:
            continue
        line = line.strip().split()
        try:
            clses.append(int(line[0]))
        except:
            continue

counter = Counter(clses)
print(counter)


