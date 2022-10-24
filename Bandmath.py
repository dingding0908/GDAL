import rasterio
from osgeo import gdal
import numpy as np
from osgeo import osr


def compute_band(file, file_ndvi_mask, result_path):
    dataset = gdal.Open(file)
    cols = dataset.RasterXSize  # 列数
    rows = dataset.RasterYSize  # 行数
    bandcount = dataset.RasterCount
    # 生成影像
    target_ds = gdal.GetDriverByName('GTiff').Create(result_path, xsize=cols, ysize=rows, bands=bandcount,
                                                     eType=gdal.GDT_Float32)
    target_ds.SetGeoTransform(dataset.GetGeoTransform())
    target_ds.SetProjection(dataset.GetProjection())

    ndviband = gdal.Open(file_ndvi_mask)
    mask = ndviband.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)

    del dataset
    for band in range(bandcount):
        dataset = gdal.Open(file)
        bandid = band + 1
        band_item = dataset.GetRasterBand(bandid).ReadAsArray(0, 0, cols, rows)
        result = np.zeros(band_item.shape, dtype=np.float32)
        cols = dataset.RasterXSize  # 列数
        rows = dataset.RasterYSize  # 行数
        for i in range(rows):
            for j in range(cols):
                result[i, j] = band_item[i, j] * mask[i, j]
        # print(result)
        # bandi = band_item +   mask
        target_ds.GetRasterBand(bandid).WriteArray(result)

    target_ds.FlushCache()


file = r'E:\Desktop\Sklearn回归模型规整\Projections\2022-07-13_3_S2DL.tif'
ndvi_mask = r'E:\Desktop\Sklearn回归模型规整\NVDI\GEE0713NVDI.tif'
compute_band(file, file_ndvi_mask=ndvi_mask, result_path='./GEE_0713_NVDImask_clip.tif')
