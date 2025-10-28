from PIL import Image, ImageChops
import numpy as np

def compare_images_percent(path_a, path_b, path_diff=None):
    a = Image.open(path_a).convert('RGB')
    b = Image.open(path_b).convert('RGB')
    if a.size != b.size:
        b = b.resize(a.size)
    diff = ImageChops.difference(a, b)
    if path_diff:
        diff.save(path_diff)
    diff_arr = np.asarray(diff)
    nonzero = np.count_nonzero(diff_arr)
    total = diff_arr.size
    percent = (nonzero / total) * 100.0
    return percent
