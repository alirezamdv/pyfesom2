#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pyfesom2` package."""

import pytest
import os
import numpy as np
import xarray as xr

from pyfesom2 import pyfesom2
from pyfesom2 import load_mesh
from pyfesom2 import get_data
from pyfesom2 import ice_ext
from pyfesom2 import ice_vol
from pyfesom2 import ice_area
from pyfesom2 import get_meshdiag
from pyfesom2 import hovm_data

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
my_data_folder = os.path.join(THIS_DIR, "data")


def test_ice_integrals():
    mesh_path = os.path.join(my_data_folder, "pi-grid")
    data_path = os.path.join(my_data_folder, "pi-results")
    mesh = load_mesh(mesh_path, usepickle=False, usejoblib=False)

    # default get_data (with how='mean') should work.

    data = get_data(data_path, "a_ice", 1948, mesh, depth=0, compute=False)
    ext = ice_ext(data, mesh)
    assert ext.data[0] == pytest.approx(12710587600895.246)

    data = get_data(data_path, "a_ice", 1948, mesh, depth=0, compute=False)
    area = ice_area(data, mesh)

    assert area.data[0] == pytest.approx(9066097785122.738)

    data = get_data(data_path, "m_ice", 1948, mesh, depth=0, compute=False)
    vol = ice_vol(data, mesh)

    assert vol.data[0] == pytest.approx(13403821068217.506)

    # work with xarray as input
    data = get_data(data_path, "a_ice", 1948, mesh, depth=0, how="ori", compute=False)
    ext = ice_ext(data, mesh)
    area = ice_area(data, mesh)

    assert ext.data[0] == pytest.approx(12710587600895.246)
    assert area.data[0] == pytest.approx(9066097785122.738)

    data = get_data(data_path, "m_ice", 1948, mesh, depth=0, how="ori", compute=False)
    vol = ice_vol(data, mesh)
    assert vol.data[0] == pytest.approx(13403821068217.506)

    # work with numpy array as input
    data = get_data(data_path, "a_ice", 1948, mesh, depth=0, how="ori", compute=True)
    ext = ice_ext(data, mesh)

    # have to load data once again, since ice_ext actually modify numpy array.
    # I don't want to add .copy to the `ice_ext` function.
    data = get_data(data_path, "a_ice", 1948, mesh, depth=0, how="ori", compute=True)
    area = ice_area(data, mesh)

    assert ext.data[0] == pytest.approx(12710587600895.246)
    assert area.data[0] == pytest.approx(9066097785122.738)

    data = get_data(data_path, "m_ice", 1948, mesh, depth=0, how="ori", compute=True)
    vol = ice_vol(data, mesh)
    assert vol.data[0] == pytest.approx(13403821068217.506)


def test_get_meshdiag():
    mesh_path = os.path.join(my_data_folder, "pi-grid")
    mesh = load_mesh(mesh_path, usepickle=False, usejoblib=False)
    diag = get_meshdiag(mesh)
    assert isinstance(diag, xr.Dataset)

    diag = get_meshdiag(mesh, meshdiag=os.path.join(mesh_path, "fesom.mesh.diag.nc"))
    assert isinstance(diag, xr.Dataset)


def test_hovm_data():
    mesh_path = os.path.join(my_data_folder, "pi-grid")
    data_path = os.path.join(my_data_folder, "pi-results")
    mesh = load_mesh(mesh_path, usepickle=False, usejoblib=False)

    # work on xarray

    # mean first, the hovm
    data = get_data(data_path, "temp", [1948, 1949], mesh, how="mean", compute=False)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (1, 47)
    assert np.nanmean(hovm) == pytest.approx(7.446110751429013)
    # hovm first, then mean
    data = get_data(data_path, "temp", [1948, 1949], mesh, how="ori", compute=False)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (2, 47)
    assert np.nanmean(hovm) == pytest.approx(7.446110751429013)

    # work on numpy array
    # mean first, the hovm
    data = get_data(data_path, "temp", [1948, 1949], mesh, how="mean", compute=True)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (1, 47)
    assert np.nanmean(hovm) == pytest.approx(7.446110751429013)
    # hovm first, then mean
    data = get_data(data_path, "temp", [1948, 1949], mesh, how="ori", compute=True)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (2, 47)
    assert np.nanmean(hovm) == pytest.approx(7.446110751429013)

    # test when only 1 time step of 3d field is in input
    data = get_data(data_path, "temp", [1948], mesh, how="mean", compute=False)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (1, 47)
    assert np.nanmean(hovm) == pytest.approx(7.440160989229884)

    data = get_data(data_path, "temp", [1948], mesh, how="mean", compute=True)
    hovm = hovm_data(data, mesh)
    assert hovm.shape == (1, 47)
    assert np.nanmean(hovm) == pytest.approx(7.440160989229884)

    # if we try to supplu 2d variable
    with pytest.raises(ValueError):
        data = get_data(data_path, "a_ice", [1948, 1949], mesh, how="mean", compute=True)
        hovm = hovm_data(data, mesh)

