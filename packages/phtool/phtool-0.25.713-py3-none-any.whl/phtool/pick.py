# -*- coding: utf-8 -*-


"""
从测光结果中选出目标星
"""


from .util import filename_split, pkl_dump, pkl_load
import numpy as np
import logging
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import os
from qmatch import match2d

def pick(
    filelist,
    offsetfile,
    pickfile,
    baseix=0,
    pickbox=20,
    xyfile=None,
):
    """
    从找到的源中选出想要进行后续较差分析的源
    :param filelist: 待处理文件列表
    :param offsetfile: 偏移文件
    :param pickfile: 星等文件
    :param baseix: 基准图像索引
    :param pickbox: 选源范围
    :param xyfile: 源位置文件
    :return: 无
    """
    logger = logging.getLogger("phtool_main")

    # 如果没有xy坐标，那么就现场读
    if xyfile and os.path.isfile(xyfile):
        bf0 = open(xyfile).readline().strip()
        x0, y0 = np.loadtxt(xyfile, unpack=True, skiprows=1)
    else:
        print("xyget")
        from .xyget import xyget
        bf0, x0, y0 = xyget(filelist, baseix=baseix, pickbox=pickbox)
    n_star = len(x0)
    if n_star == 0:
        return

    # 加载偏移
    offset_pkl = os.path.splitext(offsetfile)[0] + ".pkl"
    offset_bjd, offset_x, offset_y, offset_filelist = pkl_load(offset_pkl)
    offset_filelist = [filename_split(f)[1] for f in offset_filelist]
    offset_xd = dict(zip(offset_filelist, offset_x))
    offset_yd = dict(zip(offset_filelist, offset_y))
    offset_bjdd = dict(zip(offset_filelist, offset_bjd))

    # 校正偏移
    x0 = x0 - offset_xd.get(bf0, 0)
    y0 = y0 - offset_yd.get(bf0, 0)

    # 根据0号文件确定数据的结构，假设所有数据都是一样的孔径（要不然没法继续）
    p, bf, suff, e = filename_split(filelist[0])
    phot_pkl_file = os.path.join(p, bf + "_phot.pkl")
    sources, fwhms_med, apers, real_aper = pkl_load(phot_pkl_file)
    n_aper = len(apers)
    # 建立星等保存数组
    mag_cube = np.zeros((len(filelist), n_star, n_aper)) + np.nan  # nan表示找不到对应的星
    magerr_cube = np.zeros((len(filelist), n_star, n_aper))
    bjd = np.empty(len(filelist)) + np.nan
    bff = [filename_split(f)[1] for f in filelist]

    for k, f in enumerate(filelist):
        # 加载数据
        p, bf, suff, e = filename_split(f)
        phot_pkl_file = os.path.join(p, bf + "_phot.pkl")
        sources, fwhms_med, apers, real_aper = pkl_load(phot_pkl_file)
        # 找偏移
        xk, yk = sources["xcentroid"] + offset_xd.get(bf, 0), sources["ycentroid"] + offset_yd.get(bf, 0)
        bjd[k] = offset_bjdd.get(bf, np.nan)-2450000.0

        # 找星
        ixk, iy0 = match2d(xk, yk, x0, y0, dislimit=pickbox)
        for a in range(n_aper):
            mag_cube[k, iy0, a] = sources[ixk][f"mag_{a+1}"]
            magerr_cube[k, iy0, a] = sources[ixk][f"mag_err_{a+1}"]

    # 保存数据
    pkl_dump(pickfile, mag_cube, magerr_cube, bf0, x0, y0, apers, real_aper, bjd, bff)
    picktxt = os.path.splitext(pickfile)[0]
    for i, a in enumerate(apers):
        with open(f"{picktxt}_{a:04.1f}.txt", "w") as f:
            # 表头
            f.write(f"# {bf0}\n")
            f.write("# BJD-2450000.0\n")
            for j, (x, y) in enumerate(zip(x0, y0)):
                f.write(f"# {j+1:2d}  {x:6.1f} {y:6.1f}\n")
            # 数据
            for f in range(len(filelist)):
                f.write(f"{bjd[f]-2450000:13.7f}  \n")
                for s in range(n_star):
                    f.write(f"{mag_cube[f, s, i]:6.3f} ")
                f.write(f" {bff[i]}\n")
    # 输出日志
    logger.info(f"{n_star} sources, {n_aper} apers, {len(filelist)} files")

    # todo 把文件名、BJD等补充到输出文件，方便后面一次性调用。不同孔径输出文件名用孔径大小，不用序号
