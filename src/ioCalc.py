#
import gc

#
import numpy as np
import pandas as pd

#
import os
import rasterio as rio
import rasterstats as rstat

from eo_forge.utils.raster_utils import write_mem_raster

# Helpers


def get_ndi(
    band_1,
    band_2,
    weight=[1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    ndi_num = weight[0] * band_1.astype(dtype) - weight[1] * band_2.astype(dtype)
    ndi_den = band_1.astype(dtype) * weight[0] + band_2.astype(dtype) * weight[1]
    np.seterr(divide="ignore", invalid="ignore")
    ndi = ndi_num / ndi_den
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_zonal_stats(
    df_geom,
    raster,
    bands_list=[
        ("B02", 1),
        ("B03", 2),
        ("B04", 3),
        ("B05", 4),
        ("B8A", 5),
        ("B08", 6),
        ("B11", 7),
        ("B12", 8),
    ],
    stats=["min", "max", "mean", "median", "nodata", "range", "count"],
    ndi_ops={"ndvi": ["B08", "B04"], "ndwi": ["B03", "B08"]},
):
    """
    :param df_geom: geometry from a geodataframe
    :param raster: raster file to be queried
    :param band_list: list of tuples with (band,idx)
    :param stats: stats list to be calculated over df_geom
    """
    # iterate over bands
    band_stats = {}
    for b, i in bands_list:
        # extract only 0 element because we just feed with a single geom (by construction)
        s = rstat.zonal_stats(df_geom, raster, stats=stats, band=i)[0]
        for k in s:
            band_stats.update({b + "_" + k: s[k]})

    band_dict = dict(bands_list)

    # get ndi
    raster_10m = rio.open(raster)
    for k in ndi_ops:
        band1_num = band_dict[ndi_ops[k][0]]
        band2_num = band_dict[ndi_ops[k][1]]
        ndi = get_ndi(
            raster_10m.read(band1_num),
            raster_10m.read(band2_num),
            weight=[1, 1],
            nodata=-10000,
        )
        ndi_s = rstat.zonal_stats(
            df_geom, ndi, affine=raster_10m.transform, stats=stats, nodata=-10000
        )[0]
        for ss in ndi_s:
            band_stats.update({k + "_" + ss: ndi_s[ss]})
    raster_10m.close()
    return band_stats


def pd_get_quantiles_wcatfilter(pd_in, filt_col, target_col, rem_list=[], k_IQR=0):

    ##
    # La idea es utilizar dos columnas para referenciar, sera la que tenga las clases a filtrar
    # y la restante corresponde a la cual le vamos a calcular los quartiles
    # https://en.wikipedia.org/wiki/Outlier

    unique_f = list(pd_in[filt_col].unique())
    aux_filt = []
    Q1 = 0.25
    Q3 = 0.75
    k = k_IQR
    # [Q1-k(Q3-Q1),Q3+k(Q3-Q1)]
    q_range = [Q1, Q3]

    #
    for f in unique_f:
        f_logical = pd_in[filt_col] == f
        f_pd = pd_in.loc[f_logical, target_col].quantile(q_range)
        pd_int = pd_in.loc[f_logical, :]
        Q3_val = f_pd.values[1]
        Q1_val = f_pd.values[0]
        IQR = Q3_val - Q1_val
        f_q_l = pd_int[target_col] >= Q1_val - k * IQR
        f_q_h = pd_int[target_col] <= Q3_val + k * IQR

        f_q = np.logical_and(f_q_l, f_q_h)
        # print(pd_int[f_q])
        aux_filt.append(pd_int[f_q])
    pd_out = pd.concat(aux_filt, axis=0)
    return pd_out


def get_VARIGreen(
    band_1,
    band_2,
    band_3,
    weight=[1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]

    ndi_num = band_1 - band_2
    ndi_den = band_1 + band_2 - band_3
    np.seterr(divide="ignore", invalid="ignore")
    ndi = ndi_num / ndi_den
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_mNDVI(
    band_1,
    band_2,
    band_3,
    weight=[1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    (B08-B04)/(B08+B04-2*B02)
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]

    ndi_num = band_1 - band_2
    ndi_den = band_1 + band_2 - 2.0 * band_3
    np.seterr(divide="ignore", invalid="ignore")
    ndi = ndi_num / ndi_den
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_SIPI(
    band_1,
    band_2,
    band_3,
    weight=[1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    (B08-B02)/(B08-B04)
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]

    ndi_num = band_1 - band_2
    ndi_den = band_1 - band_3
    np.seterr(divide="ignore", invalid="ignore")
    ndi = ndi_num / ndi_den
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_EPIChlb(
    band_1,
    band_2,
    weight=[1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    """
    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]

    num = band_1
    den = band_2
    np.seterr(divide="ignore", invalid="ignore")
    epichlb = 0.0037 * (num / den) ** (1.8695)
    np.nan_to_num(epichlb, copy=False, nan=nodata)

    return epichlb


def get_OSAVI(
    band_1,
    band_2,
    weight=[1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    """
    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]

    num = band_1 - band_2
    den = band_1 + band_2 + 0.16
    np.seterr(divide="ignore", invalid="ignore")
    osavi = 1.16 * (num / den)
    np.nan_to_num(osavi, copy=False, nan=nodata)

    return osavi


def get_TCARI(
    band_1,
    band_2,
    band_3,
    weight=[1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param

    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]

    np.seterr(divide="ignore", invalid="ignore")
    ndi = 3 * ((band_1 - band_2) - 0.2 * (band_1 - band_3) * (band_1 / band_2))
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_TCARI_OSAVI(
    band_1,
    band_2,
    band_3,
    band_4,
    weight=[1.0, 1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    band_1:Band5
    band_2:Band4
    band_3:Band3
    band_4:Band8
    """
    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)
    band_4 = np.where(band_4 == bands_nodata, np.nan, band_4)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]
    band_4 = band_4.astype(dtype) * weight[3]

    tcari = 3 * ((band_1 - band_2) - 0.2 * (band_1 - band_3) * (band_1 / band_2))

    num = band_4 - band_2
    den = band_4 + band_2 + 0.16
    np.seterr(divide="ignore", invalid="ignore")
    osavi = 1.16 * (num / den)
    tcari_osavi = tcari / osavi
    np.nan_to_num(tcari_osavi, copy=False, nan=nodata)

    return tcari_osavi


def get_GARI(
    band_1,
    band_2,
    band_3,
    band_4,
    weight=[1.0, 1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    Band8−(Band3−(Band2−Band4))/[Band8−(Band3+(Band2−Band4))]
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)
    band_4 = np.where(band_4 == bands_nodata, np.nan, band_4)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]
    band_4 = band_4.astype(dtype) * weight[3]

    ndi_num = band_1 - (band_2 - (band_3 - band_4))
    ndi_den = band_1 - (band_2 + (band_3 - band_4))
    np.seterr(divide="ignore", invalid="ignore")
    ndi = ndi_num / ndi_den
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_REIP(
    band_1,
    band_2,
    band_3,
    band_4,
    weight=[1.0, 1.0, 1.0, 1.0],
    dtype=rio.float32,
    bands_nodata=0,
    nodata=-10000.0,
):
    """
    :param
    700+40*(((B04+B07)/2-B05)/(B06-B05)
    """

    band_1 = np.where(band_1 == bands_nodata, np.nan, band_1)
    band_2 = np.where(band_2 == bands_nodata, np.nan, band_2)
    band_3 = np.where(band_3 == bands_nodata, np.nan, band_3)
    band_4 = np.where(band_4 == bands_nodata, np.nan, band_4)

    band_1 = band_1.astype(dtype) * weight[0]
    band_2 = band_2.astype(dtype) * weight[1]
    band_3 = band_3.astype(dtype) * weight[2]
    band_4 = band_4.astype(dtype) * weight[3]

    ndi_num = (band_1 + band_2) / 2 - band_3
    ndi_den = band_4 - band_3
    np.seterr(divide="ignore", invalid="ignore")
    ndi = (ndi_num / ndi_den) * 40 + 700
    np.nan_to_num(ndi, copy=False, nan=nodata)

    return ndi


def get_zonal_stats_indexes(
    df_geom,
    raster,
    raster_profile=None,
    bands_list=[
        ("B02", 1),
        ("B03", 2),
        ("B04", 3),
        ("B05", 4),
        ("B06", 5),
        ("B07", 6),
        ("B8A", 7),
        ("B08", 8),
        ("B11", 9),
        ("B12", 10),
    ],
    stats=["min", "max", "mean", "median", "nodata", "range", "count"],
    **kwargs,
):
    """purpose: get some stats from raster bands

    Parameters
    -----------
        df_geom: geometry
            geometry from a geodataframe
        raster: raster path or rasterio.open instance
            raster file to be queried
        band_list: list of tuples
            list with (band,idx)
        stats: list
            stats list to be calculated over df_geom

    Returns
    -------
        band_stats: dict
            dictionary with stats over df_geom

    """
    band_dict = dict(bands_list)
    band_stats = {}

    bands_flag = kwargs.get("bands", True)
    ndi_flag = kwargs.get("ndi", True)
    mNDVI_flag = kwargs.get("mNDVI", True)
    VARIGreen_flag = kwargs.get("VARIGreen", True)
    EPIChlb_flag = kwargs.get("bands", True)
    GARI_flag = kwargs.get("GARI", True)
    REIP_flag = kwargs.get("REIP", True)
    OSAVI_flag = kwargs.get("OSAVI", True)
    TCARI_flag = kwargs.get("TCARI", True)
    TCARI_osavi_flag = kwargs.get("TCARI_osavi", True)
    SIPI_flag = kwargs.get("SIPI", True)

    #
    nodata_raster = kwargs.get("nodata_raster", 0)
    nodata_calculations = kwargs.get("nodata_calculations", -10000)

    if type(raster) == np.ndarray:
        assert raster_profile != None
        raster_10m = write_mem_raster(raster, **raster_profile)
    elif type(raster) == str:
        raster_10m = rio.open(raster)
    else:
        # assume raster
        raster_10m = raster

    if bands_flag:
        for b, i in bands_list:
            # extract only 0 element because we just feed with a single geom (by construction)
            s = rstat.zonal_stats(
                df_geom,
                raster_10m.read(i),
                affine=raster_10m.transform,
                stats=stats,
                nodata=nodata_raster,
            )[0]
            for k in s:
                band_stats.update({b + "_" + k: s[k]})
    if ndi_flag:
        # get ndi
        ndi_ops = {
            "ndvi": ["B08", "B04"],
            "ndwi": ["B03", "B08"],
            "pvr": ["B03", "B04"],
            "ndii": ["B08", "B11"],
        }
        for k in ndi_ops:
            band1_num = band_dict[ndi_ops[k][0]]
            band2_num = band_dict[ndi_ops[k][1]]
            ndi = get_ndi(
                raster_10m.read(band1_num),
                raster_10m.read(band2_num),
                weight=[1.0, 1.0],
                nodata=nodata_calculations,
            )
            ndi_s = rstat.zonal_stats(
                df_geom,
                ndi,
                affine=raster_10m.transform,
                stats=stats,
                nodata=nodata_calculations,
            )[0]
            for ss in ndi_s:
                band_stats.update({k + "_" + ss: ndi_s[ss]})
            del ndi

    if mNDVI_flag:
        # mNDVI (B08-B04)/(B08+B04-2*B02)
        band8_num = band_dict["B08"]
        band4_num = band_dict["B04"]
        band2_num = band_dict["B02"]
        B08 = raster_10m.read(band8_num)
        B04 = raster_10m.read(band4_num)
        B02 = raster_10m.read(band2_num)
        mNDVI = get_mNDVI(
            B08, B04, B02, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        mNDVI_s = rstat.zonal_stats(
            df_geom,
            mNDVI,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in mNDVI_s:
            band_stats.update({"mNDVI" + "_" + ss: mNDVI_s[ss]})
        del mNDVI

    if VARIGreen_flag:
        # VARIGreen (B03-B04)/(B03+B04-B02)
        band3_num = band_dict["B03"]
        band4_num = band_dict["B04"]
        band2_num = band_dict["B02"]
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        B02 = raster_10m.read(band2_num)

        VARIGreen = get_VARIGreen(
            B03, B04, B02, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        VARIgreen_s = rstat.zonal_stats(
            df_geom, VARIGreen, affine=raster_10m.transform, stats=stats, nodata=-10000
        )[0]
        for ss in VARIgreen_s:
            band_stats.update({"VARIGreen" + "_" + ss: VARIgreen_s[ss]})
        del VARIGreen

    if EPIChlb_flag:
        ## EPIChlb
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        epichlb = get_EPIChlb(
            B04, B03, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        epichlb_s = rstat.zonal_stats(
            df_geom,
            epichlb,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in epichlb_s:
            band_stats.update({"epichlb" + "_" + ss: epichlb_s[ss]})
        del epichlb

    if GARI_flag:
        ## GARI
        band8_num = band_dict["B08"]
        band3_num = band_dict["B03"]
        band2_num = band_dict["B02"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B03 = raster_10m.read(band3_num)
        B02 = raster_10m.read(band2_num)
        B04 = raster_10m.read(band4_num)
        gari = get_GARI(
            B08, B03, B02, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        gari_s = rstat.zonal_stats(
            df_geom,
            gari,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in gari_s:
            band_stats.update({"gari" + "_" + ss: gari_s[ss]})
        del gari

    if REIP_flag:
        # get REIP
        band4_num = band_dict["B04"]
        band7_num = band_dict["B07"]
        band5_num = band_dict["B05"]
        band6_num = band_dict["B06"]
        B04 = raster_10m.read(band4_num)
        B07 = raster_10m.read(band7_num)
        B05 = raster_10m.read(band5_num)
        B06 = raster_10m.read(band6_num)
        reip = get_REIP(
            B04, B07, B05, B06, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        reip_s = rstat.zonal_stats(
            df_geom,
            reip,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in reip_s:
            band_stats.update({"reip" + "_" + ss: reip_s[ss]})
        del reip

    if OSAVI_flag:
        # get OSAVI
        band8_num = band_dict["B08"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B04 = raster_10m.read(band4_num)
        osavi = get_OSAVI(
            B08, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        osavi_s = rstat.zonal_stats(
            df_geom,
            osavi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in osavi_s:
            band_stats.update({"osavi" + "_" + ss: osavi_s[ss]})
        del osavi

    if TCARI_flag:
        # TCARI
        band5_num = band_dict["B05"]
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        B05 = raster_10m.read(band5_num)
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        tcari = get_TCARI(
            B05, B04, B03, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        tcari_s = rstat.zonal_stats(
            df_geom,
            tcari,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in tcari_s:
            band_stats.update({"tcari" + "_" + ss: tcari_s[ss]})
        del tcari

    if TCARI_osavi_flag:
        # TCARI_osavi
        band5_num = band_dict["B05"]
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        band8_num = band_dict["B08"]
        B05 = raster_10m.read(band5_num)
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        B08 = raster_10m.read(band8_num)
        tcariOsavi = get_TCARI_OSAVI(
            B05, B04, B03, B08, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        tcariOsavi_s = rstat.zonal_stats(
            df_geom,
            tcariOsavi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in tcariOsavi_s:
            band_stats.update({"tcariOsavi" + "_" + ss: tcariOsavi_s[ss]})
        del tcariOsavi

    if SIPI_flag:
        # SIPI
        band8_num = band_dict["B08"]
        band2_num = band_dict["B02"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B02 = raster_10m.read(band2_num)
        B04 = raster_10m.read(band4_num)
        sipi = get_SIPI(
            B08, B02, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        sipi_s = rstat.zonal_stats(
            df_geom,
            sipi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )[0]
        for ss in sipi_s:
            band_stats.update({"sipi" + "_" + ss: sipi_s[ss]})
        del sipi
    raster_10m.close()
    del raster_10m
    gc.collect()
    return band_stats


def get_zonal_stats_indexes_all_geom(
    df_geom,
    raster,
    raster_profile=None,
    bands_list=[
        ("B02", 1),
        ("B03", 2),
        ("B04", 3),
        ("B05", 4),
        ("B06", 5),
        ("B07", 6),
        ("B8A", 7),
        ("B08", 8),
        ("B11", 9),
        ("B12", 10),
    ],
    stats=["min", "max", "mean", "median", "nodata", "range", "count"],
    **kwargs,
):
    """purpose: get some stats from raster bands

    Parameters
    -----------
        df_geom: geometry
            geometry from a geodataframe
        raster: raster path or rasterio.open instance
            raster file to be queried
        band_list: list of tuples
            list with (band,idx)
        stats: list
            stats list to be calculated over df_geom

    Returns
    -------
        band_stats: dict
            dictionary with stats over df_geom

    """

    def map_names(ite, name):
        return {name + "_" + k: v for k, v in ite.items()}

    band_dict = dict(bands_list)
    band_stats = []

    bands_flag = kwargs.get("bands", True)
    ndi_flag = kwargs.get("ndi", True)
    mNDVI_flag = kwargs.get("mNDVI", True)
    VARIGreen_flag = kwargs.get("VARIGreen", True)
    EPIChlb_flag = kwargs.get("bands", True)
    GARI_flag = kwargs.get("GARI", True)
    REIP_flag = kwargs.get("REIP", True)
    OSAVI_flag = kwargs.get("OSAVI", True)
    TCARI_flag = kwargs.get("TCARI", True)
    TCARI_osavi_flag = kwargs.get("TCARI_osavi", True)
    SIPI_flag = kwargs.get("SIPI", True)

    #
    nodata_raster = kwargs.get("nodata_raster", 0)
    nodata_calculations = kwargs.get("nodata_calculations", -10000)

    if type(raster) == np.ndarray:
        assert raster_profile != None
        raster_10m = write_mem_raster(raster, **raster_profile)
    else:
        raster_10m = raster

    if bands_flag:
        for b, i in bands_list:
            s = rstat.zonal_stats(
                df_geom,
                raster_10m.read(i),
                affine=raster_10m.transform,
                stats=stats,
                nodata=nodata_raster,
            )
            band_i = []
            for d in map(map_names, s, [b] * len(s)):
                band_i.append(d)
            band_stats.append(band_i)

    if ndi_flag:
        # get ndi
        ndi_ops = {
            "ndvi": ["B08", "B04"],
            "ndwi": ["B03", "B08"],
            "pvr": ["B03", "B04"],
            "ndii": ["B08", "B11"],
        }
        for b in ndi_ops:
            band1_num = band_dict[ndi_ops[b][0]]
            band2_num = band_dict[ndi_ops[b][1]]
            ndi = get_ndi(
                raster_10m.read(band1_num),
                raster_10m.read(band2_num),
                weight=[1.0, 1.0],
                nodata=nodata_calculations,
            )
            s = rstat.zonal_stats(
                df_geom,
                ndi,
                affine=raster_10m.transform,
                stats=stats,
                nodata=nodata_calculations,
            )
            band_i = []
            for d in map(map_names, s, [b] * len(s)):
                band_i.append(d)
            band_stats.append(band_i)

            del ndi

    if mNDVI_flag:
        # mNDVI (B08-B04)/(B08+B04-2*B02)
        band8_num = band_dict["B08"]
        band4_num = band_dict["B04"]
        band2_num = band_dict["B02"]
        B08 = raster_10m.read(band8_num)
        B04 = raster_10m.read(band4_num)
        B02 = raster_10m.read(band2_num)
        mNDVI = get_mNDVI(
            B08, B04, B02, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            mNDVI,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["mNDVI"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        del mNDVI

    if VARIGreen_flag:
        # VARIGreen (B03-B04)/(B03+B04-B02)
        band3_num = band_dict["B03"]
        band4_num = band_dict["B04"]
        band2_num = band_dict["B02"]
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        B02 = raster_10m.read(band2_num)

        VARIGreen = get_VARIGreen(
            B03, B04, B02, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom, VARIGreen, affine=raster_10m.transform, stats=stats, nodata=-10000
        )
        band_i = []
        for d in map(map_names, s, ["VARIGreen"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        del VARIGreen

    if EPIChlb_flag:
        ## EPIChlb
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        epichlb = get_EPIChlb(
            B04, B03, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            epichlb,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["epichlb"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        del epichlb

    if GARI_flag:
        ## GARI
        band8_num = band_dict["B08"]
        band3_num = band_dict["B03"]
        band2_num = band_dict["B02"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B03 = raster_10m.read(band3_num)
        B02 = raster_10m.read(band2_num)
        B04 = raster_10m.read(band4_num)
        gari = get_GARI(
            B08, B03, B02, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            gari,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["gari"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        del gari

    if REIP_flag:
        # get REIP
        band4_num = band_dict["B04"]
        band7_num = band_dict["B07"]
        band5_num = band_dict["B05"]
        band6_num = band_dict["B06"]
        B04 = raster_10m.read(band4_num)
        B07 = raster_10m.read(band7_num)
        B05 = raster_10m.read(band5_num)
        B06 = raster_10m.read(band6_num)
        reip = get_REIP(
            B04, B07, B05, B06, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            reip,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["reip"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        #
        del reip

    if OSAVI_flag:
        # get OSAVI
        band8_num = band_dict["B08"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B04 = raster_10m.read(band4_num)
        osavi = get_OSAVI(
            B08, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            osavi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["osavi"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        #
        del osavi

    if TCARI_flag:
        # TCARI
        band5_num = band_dict["B05"]
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        B05 = raster_10m.read(band5_num)
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        tcari = get_TCARI(
            B05, B04, B03, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            tcari,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["tcari"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)

        del tcari

    if TCARI_osavi_flag:
        # TCARI_osavi
        band5_num = band_dict["B05"]
        band4_num = band_dict["B04"]
        band3_num = band_dict["B03"]
        band8_num = band_dict["B08"]
        B05 = raster_10m.read(band5_num)
        B04 = raster_10m.read(band4_num)
        B03 = raster_10m.read(band3_num)
        B08 = raster_10m.read(band8_num)
        tcariOsavi = get_TCARI_OSAVI(
            B05, B04, B03, B08, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            tcariOsavi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["tcariOsavi"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)

        del tcariOsavi

    if SIPI_flag:
        # SIPI
        band8_num = band_dict["B08"]
        band2_num = band_dict["B02"]
        band4_num = band_dict["B04"]
        B08 = raster_10m.read(band8_num)
        B02 = raster_10m.read(band2_num)
        B04 = raster_10m.read(band4_num)
        sipi = get_SIPI(
            B08, B02, B04, bands_nodata=nodata_raster, nodata=nodata_calculations
        )
        s = rstat.zonal_stats(
            df_geom,
            sipi,
            affine=raster_10m.transform,
            stats=stats,
            nodata=nodata_calculations,
        )
        band_i = []
        for d in map(map_names, s, ["sipi"] * len(s)):
            band_i.append(d)
        band_stats.append(band_i)
        del sipi

    raster_10m.close()
    del raster_10m
    gc.collect()

    return pd.concat([pd.DataFrame(s) for s in band_stats], axis=1)


def apply_mask_return_array(raster_dataset_path, raster_mask_path, nodata=0):
    """"""
    raster_dataset = rio.open(raster_dataset_path)
    raster_mask = rio.open(raster_mask_path)

    raster_count = raster_dataset.count
    raster_mask_count = raster_mask.count
    if raster_mask_count > 1:
        assert (
            raster_count == raster_mask_count
        ), f"Raster Mask count {raster_mask_count} mismatch with raster to be masked count {raster_count}"
        read_mask = True
    else:
        read_mask = False
        mask = raster_mask.read(1).astype(bool)

    data_masked = []
    for i in raster_dataset.indexes:
        band = raster_dataset.read(i)
        if read_mask:
            mask = raster_mask.read(i).astype(bool)
        data_masked.append(np.where(mask, nodata, band))

    data = np.stack(data_masked, axis=0)

    profile = raster_dataset.profile.copy()
    profile.update(
        {
            "nodata": nodata,
        }
    )
    # clean
    raster_dataset.close()
    raster_mask.close()

    return data, profile


def get_raster_stats(raster_path, raster_cloud_path, geodataframe, stats_base="./"):
    """purpose"""
    data, profile = apply_mask_return_array(raster_path, raster_cloud_path)

    df = get_zonal_stats_indexes_all_geom(
        geodataframe.geometry.to_list(), data, raster_profile=profile
    )
    # clean
    del data
    del profile
    # misc
    base_raster = os.path.basename(raster_path)
    dataframe_path = os.path.join(stats_base, base_raster.replace(".TIF", ".csv"))
    df["raster"] = base_raster
    df.to_csv(dataframe_path)
    return None


def get_stats(geometry, raster_path):
    s = rstat.zonal_stats(
        geometry, raster_path, stats=["min", "max", "count", "nodata"]
    )[0]
    cp = (s["count"] / (s["nodata"] + s["count"])) * 100
    return cp
