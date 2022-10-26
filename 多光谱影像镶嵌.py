##交叉裁剪，交叉裁剪参数pixel_size，程序中设置200，可根据需要修改。
import numpy as np
import os
import cv2
from osgeo import gdal_array as ga

from osgeo import gdal


def write_img(filename, im_data):
    # 判断栅格数据的数据类型
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

        # 判读数组维数
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

        # 创建文件
    driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    # dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    # dataset.SetProjection(im_proj)  # 写入投影

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


if __name__ == "__main__":

    path1 = r'J:\modis\cloud_data\images_fft'  # 原始图像路径
    path2 = r'J:\modis\cloud_data\labels'  # 原始标签路径
    list = os.listdir(path1)

    img_height = 512
    img_width = 512
    g_count = 0
    # src = np.zeros((256,256))
    for k in range(len(list)):
        url = list[k]
        print(url)
        # name = url.split('data')
        # img = cv2.imread(os.path.join(path1,url),cv2.IMREAD_UNCHANGED)
        # print(img.shape)
        img = ga.LoadFile(os.path.join(path1, url))
        # img = img.swapaxes(1, 0).swapaxes(1, 2)
        print(img.shape)
        # label_name = name[0] + 'mask.tif'
        label = cv2.imread(os.path.join(path2, url), cv2.IMREAD_GRAYSCALE)  #
        print(label.shape)
        _, h, w = img.shape
        # print(h,w)
        pixel_size = 200  # 交叉步长
        num1 = (w - img_width) // pixel_size  # //取整  宽度上每隔pixel_size个像素裁剪一次
        num2 = (h - img_height) // pixel_size  # // 宽度上每隔pixel_size个像素裁剪一次
        print(num1, num2)
        yu1 = (w - img_width) % pixel_size  # %取余
        yu2 = (h - img_height) % pixel_size
        print(yu1, yu2)
        for i in range(num1 + 1):
            for j in range(num2 + 1):
                # if w -i * pixel_size + img_width < pixel_size:
                src_r1 = img[:, j * pixel_size:j * pixel_size + img_height, i * pixel_size:(i * pixel_size) + img_width]
                label_r1 = label[j * pixel_size:j * pixel_size + img_height,
                           i * pixel_size:(i * pixel_size) + img_width]
                write_img(('J:/modis/cloud_data/train_fft/images/%d.tif' % g_count), src_r1)  # 从g_count初始值开始命名
                cv2.imwrite(('J:/modis/cloud_data/train_fft/labels/%d.tif' % g_count), label_r1)
                g_count += 1
                if h - (j * pixel_size + img_height) < pixel_size:
                    src_r2 = img[:, h - img_height:h, i * pixel_size:(i * pixel_size) + img_width]
                    label_r2 = label[h - img_height:h, i * pixel_size:(i * pixel_size) + img_width]
                    write_img(('J:/modis/cloud_data/train_fft/images/%d.tif' % g_count), src_r2)  # 从g_count初始值开始命名
                    cv2.imwrite(('J:/modis/cloud_data/train_fft/labels/%d.tif' % g_count), label_r2)
                    g_count += 1
            if w - (i * pixel_size + img_width) < pixel_size:
                for k in range(num2 + 1):
                    src_r3 = img[:, k * pixel_size:k * pixel_size + img_height, w - img_width:w]
                    label_r3 = label[k * pixel_size:k * pixel_size + img_height, w - img_width:w]
                    write_img(('J:/modis/cloud_data/train_fft/images/%d.tif' % g_count), src_r3)  # 从g_count初始值开始命名
                    cv2.imwrite(('J:/modis/cloud_data/train_fft/labels/%d.tif' % g_count), label_r3)
                    g_count += 1
                    if h - (k * pixel_size + img_height) < pixel_size:
                        src_r4 = img[:, h - img_height:h, w - img_width:w]
                        label_r4 = label[h - img_height:h, w - img_width:w]
                        write_img(('J:/modis/cloud_data/train_fft/images/%d.tif' % g_count), src_r4)  # 从g_count初始值开始命名
                        cv2.imwrite(('J:/modis/cloud_data/train_fft/labels/%d.tif' % g_count), label_r4)
                        g_count += 1

    print("Successful!!!")
