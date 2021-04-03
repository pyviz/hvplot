from __future__ import absolute_import

import holoviews as _hv

from ..converter import HoloViewsConverter
from ..util import with_hv_extension
import holoviews.operation.datashader as hd 
import warnings


@with_hv_extension
def scatter_matrix(data, c=None, chart='scatter', diagonal='hist', alpha=0.5, 
    datashade=False, 
    rasterize=False,
    dynspread=False,
    spread=False,
    **kwds
    ):
    """
    Scatter matrix of numeric columns.

    Parameters:
    -----------
    data: DataFrame
    c: str, optional
        Column to color by
    chart: str, optional
        Chart type (one of 'scatter', 'bivariate', 'hexbin')
    diagonal: str, optional
        Chart type for the diagonal (one of 'hist', 'kde')
    kwds: hvplot.scatter options, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.
    """
    
    data = _hv.Dataset(data)
    supported = list(HoloViewsConverter._kind_mapping)
    if diagonal not in supported:
        raise ValueError('diagonal type must be one of: %s, found %s' %
                         (supported, diagonal))
    if chart not in supported:
        raise ValueError('Chart type must be one of: %s, found %s' %
                         (supported, chart))
    diagonal = HoloViewsConverter._kind_mapping[diagonal]
    chart = HoloViewsConverter._kind_mapping[chart]

    if rasterize:
        if dynspread or spread:
            if hd.ds_version < '0.12.0':
                raise RuntimeError('Any version of datashader ' +
                                    'less than 0.12.0 does not support ' + 
                                    'rasterize with dynspread or spread')
    #remove datashade kwds
    if datashade or rasterize:
        ds_kwds = {}
        if 'aggregator' in kwds:
            ds_kwds['aggregator'] = kwds.pop('aggregator')
        
    #remove dynspread kwds
    sp_kwds={}
    if dynspread:
        if datashade == False and rasterize == False:
            warnings.warn(
                "Datashade or Rasterize must be specified to use dynspread. " 
                "Dynspread will not be applied to plots."
                )

        if 'max_px' in kwds:
            sp_kwds['max_px'] = kwds.pop('max_px')
        if 'threshold' in kwds:
            sp_kwds['threshold'] = kwds.pop('threshold')
        if 'how' in kwds:
            sp_kwds['how'] = kwds.pop('how')
        if 'mask' in kwds:
            sp_kwds['mask'] = kwds.pop('mask')
            

    if spread:
        if datashade == False and rasterize == False:
            warnings.warn(
                "Datashade or Rasterize must be specified to use spread. " 
                "Spread will not be applied to plots."
                )
        if 'px' in kwds:
            sp_kwds['px'] = kwds.pop('px')
        if 'shape' in kwds:
            sp_kwds['shape'] = kwds.pop('shape')
        if 'how' in kwds:
            sp_kwds['how'] = kwds.pop('how')
        if 'mask' in kwds:
            sp_kwds['mask'] = kwds.pop('mask')
            
        

    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    chart_opts = dict(alpha=alpha, cmap=colors, tools=['box_select', 'lasso_select'],
                      nonselection_alpha=0.1, **kwds)

    #get initial scatter matrix.  No color.
    grid = _hv.operation.gridmatrix(data, diagonal_type=diagonal, chart_type=chart)

    if c:
        #change colors for scatter matrix
        chart_opts['color_index'] = c
        # Add color vdim to each plot.
        grid = grid.map(lambda x: x.clone(vdims=x.vdims+[c]), 'Scatter')
        # create a new scatter matrix with groups for each catetory, so now the histogram will
        # show separate colors for each group.
        groups = _hv.operation.gridmatrix(data.groupby(c).overlay(),
                                          chart_type=chart,
                                          diagonal_type=diagonal)
        # take the correct layer from each Overlay object within the scatter matrix.
        grid = (grid * groups).map(lambda x: x.get(0) if isinstance(x.get(0), chart) else x.get(1),
                                   _hv.Overlay)

    # set the histogram colors 
    diagonal_opts = {'fill_color': _hv.Cycle(values=colors)}
    # actually changing to the same color scheme for both scatter and histogram plots.
    grid = grid.options({chart.__name__: chart_opts, diagonal.__name__: diagonal_opts})
    
    # Perform datashade options after all the coloring is finished.
    if datashade or rasterize:
        aggregatefn = hd.datashade if datashade else hd.rasterize
        spreadfn    = hd.dynspread if dynspread else (hd.spread if spread else lambda z, **_: z)
    
        grid = grid.map(lambda x: x.apply(aggregatefn, **ds_kwds).apply(spreadfn, **sp_kwds) if isinstance(x, chart) else x)


   
    return grid
