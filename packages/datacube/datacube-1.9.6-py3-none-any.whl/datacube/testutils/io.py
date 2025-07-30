# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import toolz
import xarray
from odc.geo import wh_
from odc.geo.geobox import GeoBox, zoom_to
from odc.geo.warp import resampling_s2rio
from odc.geo.xr import xr_coords
from typing_extensions import override

from ..index.eo3 import EO3Grid, is_doc_eo3
from ..model import Dataset
from ..storage import BandInfo, reproject_and_fuse
from ..storage._read import rdr_geobox
from ..storage._rio import RasterDatasetDataSource, RasterioDataSource
from . import suppress_deprecations


class RasterFileDataSource(RasterioDataSource):
    """This is only used in test code"""

    def __init__(
        self, filename, bandnumber, nodata=None, crs=None, transform=None, lock=None
    ) -> None:
        super().__init__(filename, nodata, lock=lock)
        self.bandnumber = bandnumber
        self.crs = crs
        self.transform = transform

    @override
    def get_bandnumber(self, src):
        return self.bandnumber

    @override
    def get_transform(self, shape):
        if self.transform is None:
            raise RuntimeError("No transform in the data and no fallback")
        return self.transform

    @override
    def get_crs(self):
        if self.crs is None:
            raise RuntimeError("No CRS in the data and no fallback")
        return self.crs


def _raster_metadata(band):
    source = RasterDatasetDataSource(band)
    with source.open() as rdr:
        return SimpleNamespace(
            dtype=rdr.dtype.name, nodata=rdr.nodata, geobox=rdr_geobox(rdr)
        )


def get_raster_info(
    ds: Dataset, measurements: list[str] | None = None
) -> dict[str, Any]:
    """
    :param ds: Dataset
    :param measurements: List of band names to load
    """
    if measurements is None:
        measurements = list(ds.product.measurements)

    return {n: _raster_metadata(BandInfo(ds, n)) for n in measurements}


def eo3_geobox(ds: Dataset, band: str | None = None, grid: str = "default") -> GeoBox:
    if band is not None:
        mm = ds.measurements.get(ds.product.canonical_measurement(band), None)
        if mm is None:
            raise ValueError(f"No such band: {band}")
        grid = mm.get("grid", "default")

    crs = ds.crs
    doc_path = ("grids", grid)

    grid_spec = toolz.get_in(doc_path, ds.metadata_doc)
    if crs is None or grid_spec is None:
        raise ValueError("Not a valid EO3 dataset")

    parsed = EO3Grid(grid_spec)
    return GeoBox(parsed.shape, parsed.transform, crs)


def native_geobox(ds: Dataset, measurements=None, basis: str | None = None):
    """Compute native GeoBox for a set of bands for a given dataset

    :param ds: Dataset
    :param measurements: List of band names to consider
    :param basis: Name of the band to use for computing reference frame, other
    bands might be reprojected if they use different pixel grid

    :return: GeoBox describing native storage coordinates.
    """
    with suppress_deprecations():
        gs = ds.product.grid_spec
        if gs is not None:
            # Dataset is from ingested product, figure out GeoBox of the tile this dataset covers
            bb = [gbox for _, gbox in gs.tiles(ds.bounds)]
            if len(bb) != 1:
                # Ingested product but dataset overlaps several/none tiles -- no good
                raise ValueError("Broken GridSpec detected")
            return bb[0]

    if measurements is None and basis is None:
        measurements = list(ds.product.measurements)

    if is_doc_eo3(ds.metadata_doc):
        if basis is not None:
            return eo3_geobox(ds, basis)

        gboxes = [eo3_geobox(ds, band) for band in measurements]
    else:
        if basis is not None:
            return get_raster_info(ds, [basis])[basis].geobox

        ii = get_raster_info(ds, measurements)
        gboxes = [info.geobox for info in ii.values()]

    geobox = gboxes[0]
    consistent = all(geobox == gbox for gbox in gboxes)
    if not consistent:
        raise ValueError("Not all bands share the same pixel grid")
    return geobox


def native_load(ds, measurements=None, basis=None, **kw):
    """Load single dataset in native resolution.

    :param ds: Dataset
    :param measurements: List of band names to load
    :param basis: Name of the band to use for computing reference frame, other
    bands might be reprojected if they use different pixel grid

    :param kw: Any other parameter load_data accepts

    :return: Xarray dataset
    """
    from datacube import Datacube

    geobox = native_geobox(
        ds, measurements, basis
    )  # early exit via exception if no compatible grid exists
    if measurements is not None:
        mm = ds.product.lookup_measurements(measurements)
    else:
        mm = ds.product.measurements

    return Datacube.load_data(
        Datacube.group_datasets([ds], "time"), geobox, measurements=mm, **kw
    )


def dc_read(
    path,
    band: int = 1,
    geobox=None,
    resampling: str = "nearest",
    dtype=None,
    dst_nodata: float | None = None,
    fallback_nodata=None,
):
    """
    Use default io driver to read file without constructing Dataset object.
    """
    source = RasterFileDataSource(path, band, nodata=fallback_nodata)
    with source.open() as rdr:
        dtype = rdr.dtype if dtype is None else dtype
        if geobox is None:
            geobox = rdr_geobox(rdr)
        if dst_nodata is None:
            dst_nodata = rdr.nodata

    # currently dst_nodata = None case is not supported. So if fallback_nodata
    # was None and file had none set, then use 0 as default output fill value
    if dst_nodata is None:
        dst_nodata = 0

    im = np.full(geobox.shape, dst_nodata, dtype=dtype)
    reproject_and_fuse([source], im, geobox, dst_nodata, resampling=resampling)
    return im


def write_gtiff(
    fname: Path,
    pix,
    crs: str = "epsg:3857",
    resolution=(10, -10),
    offset: tuple[float, float] = (0.0, 0.0),
    nodata=None,
    overwrite: bool = False,
    blocksize: int | None = None,
    geobox=None,
    **extra_rio_opts,
) -> SimpleNamespace:
    """Write ndarray to GeoTiff file.

    Geospatial info can be supplied either via
    - resolution, offset, crs
    or
    - geobox (takes precedence if supplied)
    """
    # pylint: disable=too-many-locals

    from pathlib import Path

    import rasterio
    from affine import Affine

    if pix.ndim == 2:
        h, w = pix.shape
        nbands = 1
        band: int | tuple[int, ...] = 1
    elif pix.ndim == 3:
        nbands, h, w = pix.shape
        band = tuple(i for i in range(1, nbands + 1))
    else:
        raise ValueError("Need 2d or 3d ndarray on input")

    if not isinstance(fname, Path):
        fname = Path(fname)

    if fname.exists():
        if overwrite:
            fname.unlink()
        else:
            raise OSError("File exists")

    if geobox is not None:
        assert geobox.shape == (h, w)

        A = geobox.transform
        crs = str(geobox.crs)
    else:
        sx, sy = resolution
        tx, ty = offset

        A = Affine(sx, 0, tx, 0, sy, ty)

    rio_opts = {
        "width": w,
        "height": h,
        "count": nbands,
        "dtype": pix.dtype.name,
        "crs": crs,
        "transform": A,
        "predictor": 2,
        "compress": "DEFLATE",
    }

    if blocksize is not None:
        rio_opts.update(
            tiled=True, blockxsize=min(blocksize, w), blockysize=min(blocksize, h)
        )

    if nodata is not None:
        rio_opts.update(nodata=nodata)

    rio_opts.update(extra_rio_opts)

    with rasterio.open(str(fname), "w", driver="GTiff", **rio_opts) as dst:
        dst.write(pix, band)
        meta = dst.meta

    meta["geobox"] = geobox if geobox is not None else rio_geobox(meta)
    meta["path"] = fname
    return SimpleNamespace(**meta)


def dc_crs_from_rio(crs):
    from odc.geo import CRS

    if crs.is_epsg_code:
        return CRS(f"EPSG:{crs.to_epsg()}")
    return CRS(crs.wkt)


def rio_geobox(meta):
    """Construct geobox from src.meta of opened rasterio dataset"""
    if "crs" not in meta or "transform" not in meta:
        return None

    h, w = (meta["height"], meta["width"])
    crs = dc_crs_from_rio(meta["crs"])
    transform = meta["transform"]

    return GeoBox(wh_(w, h), transform, crs)


def _fix_resampling(kw: dict) -> None:
    r = kw.get("resampling", None)
    if isinstance(r, str):
        kw["resampling"] = resampling_s2rio(r)


def rio_slurp_reproject(fname, geobox, dtype=None, dst_nodata=None, **kw):
    """
    Read image with reprojection
    """
    import rasterio
    from rasterio.warp import reproject

    _fix_resampling(kw)

    with rasterio.open(str(fname), "r") as src:
        if src.count == 1:
            shape = geobox.shape
            src_band = rasterio.band(src, 1)
        else:
            shape = (src.count, *geobox.shape)
            src_band = rasterio.band(src, tuple(range(1, src.count + 1)))

        if dtype is None:
            dtype = src.dtypes[0]
        if dst_nodata is None:
            dst_nodata = src.nodata
        if dst_nodata is None:
            dst_nodata = 0

        pix = np.full(shape, dst_nodata, dtype=dtype)

        reproject(
            src_band,
            pix,
            dst_nodata=dst_nodata,
            dst_transform=geobox.transform,
            dst_crs=str(geobox.crs),
            **kw,
        )

        meta = src.meta
        meta["src_geobox"] = rio_geobox(meta)
        meta["path"] = fname
        meta["geobox"] = geobox

        return pix, SimpleNamespace(**meta)


def rio_slurp_read(fname, out_shape=None, **kw):
    """
    Read whole image file using rasterio.

    :returns: ndarray (2d or 3d if multi-band), dict (rasterio meta)
    """
    import rasterio

    _fix_resampling(kw)

    if out_shape is not None:
        kw.update(out_shape=out_shape)

    with rasterio.open(str(fname), "r") as src:
        data = src.read(1, **kw) if src.count == 1 else src.read(**kw)
        meta = src.meta
        src_geobox = rio_geobox(meta)

        same_geobox = out_shape is None or out_shape == src_geobox.shape
        geobox = src_geobox if same_geobox else zoom_to(src_geobox, out_shape)

        meta["src_geobox"] = src_geobox
        meta["geobox"] = geobox
        meta["path"] = fname
        return data, SimpleNamespace(**meta)


def rio_slurp(fname, *args, **kw):
    """
    Dispatches to either:

    rio_slurp_read(fname, out_shape, ..)
    rio_slurp_reproject(fname, geobox, ...)
    """
    if len(args) == 0:
        if "geobox" in kw:
            return rio_slurp_reproject(fname, **kw)
        else:
            return rio_slurp_read(fname, **kw)

    if isinstance(args[0], GeoBox):
        return rio_slurp_reproject(fname, *args, **kw)
    else:
        return rio_slurp_read(fname, *args, **kw)


def rio_slurp_xarray(fname, *args, rgb: str = "auto", **kw) -> xarray.DataArray:
    """
    Dispatches to either:

    rio_slurp_read(fname, out_shape, ..)
    rio_slurp_reproject(fname, geobox, ...)

    then wraps it all in xarray.DataArray with .crs,.nodata etc.
    """
    from xarray import DataArray

    if len(args) == 0:
        if "geobox" in kw:
            im, mm = rio_slurp_reproject(fname, **kw)
        else:
            im, mm = rio_slurp_read(fname, **kw)
    else:
        if isinstance(args[0], GeoBox):
            im, mm = rio_slurp_reproject(fname, *args, **kw)
        else:
            im, mm = rio_slurp_read(fname, *args, **kw)

    if im.ndim == 3:
        dims = ("band", *mm.geobox.dims)
        if rgb and im.shape[0] in (3, 4):
            im = im.transpose([1, 2, 0])
            dims = tuple(dims[i] for i in [1, 2, 0])
    else:
        dims = mm.geobox.dims

    return DataArray(
        im, dims=dims, coords=xr_coords(mm.geobox), attrs={"nodata": mm.nodata}
    )
