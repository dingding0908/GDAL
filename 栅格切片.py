import os
from curses import window
from operator import index
import rasterio
from rasterio.windows import Window
from tqdm import tqdm


def get_files(root_files):
    '''
    root_files:图像存储目录
    return:图像文件名列表
    '''
    files_name = []
    for root, dirs, file in os.walk(root_files):
        for i in range(len(file)):
            file_name = os.path.join(root_files, file[i])
            files_name.append(file_name)
    return files_name


def clip_image(save_root, files_name, image_width, image_height, Clip_width, Clip_height):
    '''
    save_root:文件保存目录
    files_name:文件名称，get_files(root_files)的返回值
    image_width,image_height：原图的宽和高
    Clip_width,Clip_height：裁剪模板的宽和高
    '''
    col_num = int(image_width / Clip_width)
    row_num = int(image_height / Clip_height)
    for f in tqdm(range(len(files_name)), desc='Total process'):
        windows = []
        windows_transform = []
        with rasterio.open(files_name[f]) as src:
            for i in range(row_num):
                for j in range(col_num):
                    win = Window(j * Clip_width, i * Clip_height, Clip_width, Clip_height)
                    windows.append(win)
                    win_transform = src.window_transform(win)
                    # 重算仿射变换矩阵
                    windows_transform.append(win_transform)
            for win in tqdm(range(len(windows)), desc="Single progress", leave=False):
                k = 1
                bands_array = []
                for c in range(src.count):
                    band_array = src.read(c + 1, window=windows[win])
                    bands_array.append(band_array)
                dst = rasterio.open(
                    os.path.join(save_root, os.path.splitext(os.path.split(files_name[f])[1])[0] + "_" + str(win + 1) +
                                 os.path.splitext(files_name[f])[1]),
                    'w',
                    driver='GTiff',
                    width=Clip_width, height=Clip_height, count=src.count,
                    crs=src.crs,
                    transform=windows_transform[win],
                    dtype=band_array.dtype)
                for arr in bands_array:
                    dst.write(arr, indexes=k)
                    k += 1
