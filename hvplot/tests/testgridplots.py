from unittest import SkipTest
from collections import OrderedDict

import numpy as np
from holoviews import Store
from holoviews.element import RGB, Image
from holoviews.element.comparison import ComparisonTestCase

try:
    import xarray as xr
except:
    raise SkipTest('XArray not available')
else:
    import hvplot.xarray

class TestGridPlots(ComparisonTestCase):

    def setUp(self):
        coords = OrderedDict([('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb = xr.DataArray(np.arange(12).reshape((3, 2, 2)),
                                   coords, ['band', 'y', 'x'])
        coords = OrderedDict([('time', [0, 1]), ('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb_by_time = xr.DataArray(np.arange(24).reshape((2, 3, 2, 2)),
                                           coords, ['time', 'band', 'y', 'x'])

        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(np.arange(8).reshape((2, 2, 2)),
                                           coords, ['time', 'lat', 'lon']).assign_coords(
                                               lat1=xr.DataArray([2,3], dims=['lat']))

        self.xarr_with_attrs = xr.DataArray(
            np.random.rand(10, 10), coords=[('x', range(10)), ('y', range(10))],
            dims=['y', 'x'], attrs={'long_name': 'luminosity', 'units': 'lm'})
        self.xarr_with_attrs.x.attrs['long_name'] = 'Declination'
        self.xarr_with_attrs.y.attrs['long_name'] = 'Right Ascension'

        self.xds_with_attrs = xr.Dataset({'light': self.xarr_with_attrs })
        self.da_img = xr.DataArray(np.arange(-2, 2).reshape((2, 2)), name='foo')

    def test_rgb_dataarray_no_args(self):
        rgb = self.da_rgb.hvplot()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args(self):
        rgb = self.da_rgb.hvplot('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args_and_kind(self):
        rgb = self.da_rgb.hvplot.rgb('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataset(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataset_explicit_z(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb(z='z')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_groupby_explicit(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', groupby='time')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[1])))

    def test_rgb_dataarray_groupby_infer(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', bands='band')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[1])))

    def test_img_dataarray_infers_correct_other_dims(self):
        img = self.da_img_by_time[0].hvplot()
        self.assertEqual(img, Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))

    def test_img_dataarray_groupby_infers_correct_other_dims(self):
        img = self.da_img_by_time.hvplot(groupby='time')
        self.assertEqual(img[0], Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))
        self.assertEqual(img[1], Image(self.da_img_by_time[1], ['lon', 'lat'], ['value']))

    def test_line_infer_dimension_params_from_xarray_attrs(self):
        hmap = self.xarr_with_attrs.hvplot.line(groupby='x', dynamic=False)
        self.assertEqual(hmap.kdims[0].label, 'Declination')
        self.assertEqual(hmap.last.kdims[0].label, 'Right Ascension')
        self.assertEqual(hmap.last.vdims[0].label, 'luminosity')
        self.assertEqual(hmap.last.vdims[0].unit, 'lm')

    def test_img_infer_dimension_params_from_xarray_attrs(self):
        img = self.xarr_with_attrs.hvplot.image(clim=(0, 2))
        self.assertEqual(img.kdims[0].label, 'Declination')
        self.assertEqual(img.kdims[1].label, 'Right Ascension')
        self.assertEqual(img.vdims[0].label, 'luminosity')
        self.assertEqual(img.vdims[0].unit, 'lm')
        self.assertEqual(img.vdims[0].range, (0, 2))

    def test_table_infer_dimension_params_from_xarray_ds_attrs(self):
        table = self.xds_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.kdims[2].label, 'luminosity')
        self.assertEqual(table.kdims[2].unit, 'lm')

    def test_points_infer_dimension_params_from_xarray_attrs(self):
        points = self.xarr_with_attrs.hvplot.points(c='value', clim=(0, 2))
        self.assertEqual(points.kdims[0].label, 'Declination')
        self.assertEqual(points.kdims[1].label, 'Right Ascension')
        self.assertEqual(points.vdims[0].label, 'luminosity')
        self.assertEqual(points.vdims[0].unit, 'lm')
        self.assertEqual(points.vdims[0].range, (0, 2))

    def test_dataset_infer_dimension_params_from_xarray_attrs(self):
        ds = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(ds.kdims[0].label, 'Declination')
        self.assertEqual(ds.kdims[1].label, 'Right Ascension')
        self.assertEqual(ds.kdims[2].label, 'luminosity')
        self.assertEqual(ds.kdims[2].unit, 'lm')

    def test_table_infer_dimension_params_from_xarray_attrs(self):
        table = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.kdims[2].label, 'luminosity')
        self.assertEqual(table.kdims[2].unit, 'lm')

    def test_symmetric_img_deduces_symmetric(self):
        plot = self.da_img.hvplot.image()
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_img_with_symmetric_set_to_false(self):
        plot = self.da_img.hvplot.image(symmetric=False)
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_symmetric_img_with_cmap_set(self):
        plot = self.da_img.hvplot.image(cmap='fire')
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'fire')
