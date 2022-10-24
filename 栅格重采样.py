# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 23:32:25 2020
以栅格A参考，对栅格B进行重投影操作，输出结果和栅格A尺寸一样，像元也相互对齐
https://gis.stackexchange.com/questions/234022/resampling-a-raster-from-python-without-using-gdalwarp
https://gis.stackexchange.com/questions/268119/how-can-2-geotiff-rasters-be-aligned-and-forced-to-have-same-resolution-in-pytho
@author: pan
"""
from osgeo import gdal
from osgeo import gdalconst

TheFirstfilepath = r'E:\Desktop\LAI回归模型训练\00LAI0713\LAI_whole_0713.tif'
TheSecondefilepath = r'E:\Desktop\LAI回归模型训练\06GEE_CLIP\GEE_clip_0713.tif'
outputfilepath = r'E:\Desktop\LAI回归模型训练\03ResamplingLAI0713\LAI_0713_resampling6.tif'
# 打开tif文件
ref_ds = gdal.Open(TheSecondefilepath, gdalconst.GA_ReadOnly)  # 参考文件
in_ds = gdal.Open(TheFirstfilepath, gdalconst.GA_ReadOnly)  # 输入文件
# 打印部分文件信息
print(in_ds.RasterXSize, in_ds.RasterYSize, ref_ds.RasterXSize, ref_ds.RasterYSize)
print('******test1 info:******', gdal.Info(ref_ds))
print('******test2 info:******', gdal.Info(in_ds))

# 参考文件与输入文件的的地理仿射变换参数与投影信息
in_trans = in_ds.GetGeoTransform()
in_proj = in_ds.GetProjection()
ref_trans = ref_ds.GetGeoTransform()
ref_proj = ref_ds.GetProjection()
# 参考文件的波段参考信息
band_ref = ref_ds.GetRasterBand(1)
# 参考文件行列数
x = ref_ds.RasterXSize
y = ref_ds.RasterYSize

# 创建输出文件
driver = gdal.GetDriverByName('GTiff')
output = driver.Create(outputfilepath, x, y, 1, band_ref.DataType)
# 设置输出文件地理仿射变换参数与投影
output.SetGeoTransform(ref_trans)
output.SetProjection(ref_proj)

# 重投影，插值方法为双线性内插法
gdal.ReprojectImage(in_ds, output, in_proj, ref_proj, gdalconst.GRA_Bilinear)

# 关闭数据集与driver
in_ds1 = None
in_ds2 = None
drive = None
output = None
