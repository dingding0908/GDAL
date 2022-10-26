import os
from osgeo import gdal
import numpy as np
import gdalconst, gdal, ogr, osr
def read_img(filename):
    dataset = gdal.Open(filename)  # 打开文件
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数

    im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
    im_proj = dataset.GetProjection()  # 地图投影信息
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵

    del dataset  # 关闭对象，文件dataset
    return im_proj, im_geotrans, im_data, im_width, im_height

def write_img(filename, im_proj, im_geotrans, im_data):

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
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype) #options=["INTERLEAVE=BAND"]

    dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    dataset.SetProjection(im_proj)  # 写入投影

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset

def raster2polygon(path):

    #savepath = 'J:/modis/2014/select/binary/2/'
    filelist = os.listdir(path)
    for file in filelist:
        #mask = cv2.imread(path + file,cv2.IMREAD_UNCHANGED)
        #mask = mask * 255
        im_proj, im_geotrans, im_data, im_width, im_height = read_img(path + file)
        # #print(mask)
        # im_data = np.where(im_data>0.2,1,0)
        # #mask = np.where(mask > 0.2, 1, 0)
        # write_img(savepath + file,im_proj,im_geotrans,im_data)
        #cv2.imwrite(savepath + file,mask)
        prj = osr.SpatialReference()
        prj.ImportFromWkt(im_proj)
        input = path + file
        inraster = gdal.Open(input)  # 读取路径中的栅格数据
        inband = inraster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1

        output_shp = input[:-4] + ".shp"  # 给后面生成的矢量准备一个输出文件名，这里就是把原栅格的文件名后缀名改成shp了
        drv = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(output_shp):  # 若文件已经存在，则删除它继续重新做一遍
            drv.DeleteDataSource(output_shp)
        Polygon = drv.CreateDataSource(output_shp)  # 创建一个目标文件
        Poly_layer = Polygon.CreateLayer(input[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
        newField = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
        Poly_layer.CreateField(newField)
        Type = ogr.FieldDefn('type', ogr.OFTString)
        Poly_layer.CreateField(Type)

        gdal.FPolygonize(inband, None, Poly_layer, 0)  # 核心函数，执行的就是栅格转矢量操作
        del inraster
        del inband
        Polygon.SyncToDisk()
        Polygon = None
        datasource = drv.Open(output_shp, 1)
        layer = datasource.GetLayer(0)
        defn = layer.GetLayerDefn()

if __name__ == "__main__":

    path = 'J:/modis/2014/select/binary/2/'
    raster2polygon(path)