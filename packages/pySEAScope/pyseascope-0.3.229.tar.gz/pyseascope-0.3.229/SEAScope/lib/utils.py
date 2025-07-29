# vim: set ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
#
# This file is part of SEAScope, a 3D visualisation and analysis application
# for satellite, in-situ and numerical model data.
#
# Copyright (C) 2014-2023 OceanDataLab
#
# SEAScope is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SEAScope is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with SEAScope. If not, see <https://www.gnu.org/licenses/>.

"""
This module provides methods for creating and reformatting data structures.
"""
import math
import logging
import datetime

logger = logging.getLogger(__name__)


class DynamicPackingFloatIncompatbilityError(Exception):
    """Raised when :func:`SEAScope.lib.utils.set_field` is called with both
    ``dynamic_packing`` and ``as_float`` set to True`: dynamic packing is only
    implemented for unsigned bytes"""
    pass


class InvalidShapeError(ValueError):
    """Raised when the shape passed to :func:`SEAScope.lib.utils.get_lonlat`
    does not have exactly 2 elements (shape for a 2D matrix)."""
    pass


class FieldShapeError(ValueError):
    """Raised when the data associated with a field is neither 1D nor 2D."""
    pass


class IncompatibleFieldError(ValueError):
    """Raised when a field cannot be added to a granule because it is not
    compatible with already attached fields (shape mismatch)."""
    pass


def _id_generator(offset):
    """"""
    for value in range(offset, 100000):
        yield value


collection_id_generator = _id_generator(10)
granule_id_generator = _id_generator(1000)


def init_ids(collection_offset, granule_offset):
    """Initialize the local, i.e. specific to current data source, identifiers
    generators for collections and granules.

    Parameters
    ----------
    collection_offset : int
        Initial value for the collection identifiers generator. Please note
        that the initial value cannot be less than 3 because identifiers "1"
        and "2" are reserved for the "User polygons" and "User polylines"
        collections that SEAScope creates automatically (these two collections
        share the same source as the ones you create using the Python bindings)
    granule_offset : int
        Initial value for the granule identifiers generator. Please note that
        the initial value cannot be less than 1000 so that SEAScope has enough
        reserved identifiers for the polygons and polylines drawn by the user.
    """
    global collection_id_generator
    global granule_id_generator

    # collection IDs 1 and 2 are reserved for polygons and polylines
    if collection_offset < 3:
        collection_offset = 3
        logger.warning('Collection IDs 1 and 2 are reserved for internal use '
                       'in SEAScope. Your input has been modified to prevent '
                       'issues: collection_offset = 3')

    # Reserve 1000 granule IDs for the polygons and polylines the user will
    # draw in SEAScope
    if granule_offset < 1000:
        granule_offset = 1000
        logger.warning('Granule IDs below 1000 are reserved for internal use '
                       'in SEAScope. Your input has been modified to prevent '
                       'issues: granule_offset = 1000')

    collection_id_generator = _id_generator(collection_offset)
    granule_id_generator = _id_generator(granule_offset)


def create_collection(label):
    """Helper method to create the dictionary that represents a collection.

    Most fields are initialized with default values that you can/should
    customize before passing the generated dictionary to other methods.

    Parameters
    ----------
    label : str
        Label describing the collection. This is the text that SEAScope will
        display in the catalogue for this collection.

    Returns
    -------
    tuple(int, dict)
        A tuple which contains two elements:

          - an integer which is the local identifier, i.e. the identifier
            within a source, for the collection

          - a dictionary which contains all the information SEAScope needs to
            identify and format data associated with the collection variables.

    Example
    -------
    >>> import SEAScope.lib.utils
    >>> result = SEAScope.lib.utils.create_collection('A custom collection')
    >>> coll_id, coll_dict = result
    >>> print(coll_id)
    10
    >>> print(coll_dict)
    {'id': {'granuleLevel': False,
            'sourceId': 1,
            'collectionId': 10,
            'granuleId': 0,
            'variableId': 0},
     'mustBeCurrent': False,
     'xSeamless': False,
     'ySeamless': False,
     'NEWSAligned': False,
     'label': 'A custom collection',
     'tags': {},
     'variables': [],
     'variablesList': {},
     'defaultVariable': 0}
    """
    unique_id = next(collection_id_generator)
    _rid = {'granuleLevel': False,
            'sourceId': 1,
            'collectionId': unique_id,
            'granuleId': 0,
            'variableId': 0}
    result = {'id': _rid,
              'mustBeCurrent': False,
              'xSeamless': False,
              'ySeamless': False,
              'NEWSAligned': False,
              'label': label,
              'tags': {},
              'variables': [],
              'variablesList': {},
              'defaultVariable': 0}
    return unique_id, result


def create_variable(collection, label, fields, units='', dims=2):
    """Helper method to create the dictionary that represents a variable.

    Most fields are initialized with default values that you can/should
    customize before passing the generated dictionary to other methods.

    Parameters
    ----------
    collection : dict
        Dictionary which represents a collection. This dictionary is either
        handcrafted or generated by the :func:`create_collection` method.
    label : str
        Label describing the variable. This is the text that will be displayed
        in the SEAScope catalogue.
    units : str
        Units of the geophysical data contained in the variable. Defaults to an
        empty string.
    dims : int
        Number of dimensions of the data matrix associated with the variable.
        If this parameter is set to 1 the default rendering method for this
        variable will be TRAJECTORIES, otherwise it will be RASTER.

    Returns
    -------
    dict
        A dictionary which contains all the information SEAScope needs to
        identify the variable and render the associated data.

    Example
    -------
    >>> import SEAScope.lib.utils
    >>> result = SEAScope.lib.utils.create_collection('A custom collection')
    >>> coll_id, coll_dict = result
    >>> var_dict = SEAScope.lib.utils.create_variable(coll_dict, 'my variable',
    >>>                                               ['u_field', 'v_field'],
    >>>                                               'm.s-1')
    >>> print(var_dict)
    {'id': 0,
     'label': 'my variable',
     'units': 'm.s-1',
     'fields': ['u_field', 'v_field'],
     'defaultRenderingMethod': 'RASTER',
     'tags': {},
     'collection': {'granuleLevel': False,
                    'sourceId': 1,
                    'collectionId': 10,
                    'granuleId': 0,
                    'variableId': 0},
     'rendering': {'rendered': True,
                   'logscale': False,
                   'min': 0,
                   'max': 1,
                   'opacity': 1.0,
                   'zindex': 500,
                   'color': [50, 12, 87],
                   'colormap': 'grayscale',
                   'renderMethod': 'RASTER',
                   'particlesCount': 1000,
                   'particleTTL': 10,
                   'streamlineLength': 20,
                   'streamlineSpeed': 0.0,
                   'filterMode': 'NEAREST',
                   'target': {'granuleLevel': False,
                              'sourceId': 1,
                              'collectionId': 10,
                              'granuleId': 0,
                              'variableId': 0}}}
    """
    if label in collection['variablesList']:
        var_id = collection['variablesList'][label]
        logger.warn('Variable "{}" already exists for this collection and has '
                    'identifier "{}"'.format(label, var_id))
        return None

    unique_id = len(collection['variablesList'].keys())
    collection['variablesList'][label] = unique_id

    rcfg = create_rendering_config(collection['id']['collectionId'], unique_id)
    r_method = 'RASTER'
    if 1 == dims:
        r_method = 'TRAJECTORIES'
    rcfg['renderMethod'] = r_method

    result = {'id': unique_id,
              'label': label,
              'units': units,
              'fields': fields,
              'defaultRenderingMethod': r_method,
              'tags': {},
              'collection': collection['id'],
              'rendering': rcfg}
    return result


def create_rendering_config(col_id=0, var_id=0):
    """Helper method to create the dictionary that represents a rendering
    configuration (for a variable).

    Most fields are initialized with default values that you can/should
    customize before passing the generated dictionary to other methods.

    Parameters
    ----------
    col_id : int
        Local (i.e. specifc to the current data source) identifier for the
        collection
    var_id : int
        Identifier for the variable within the collection

    Returns
    -------
    dict
        A dictionary which contains the rendering parameters to use for the
        variable which corresponds to the (col_id, var_id) couple.

    Example
    -------
    >>> import SEAScope.lib.utils
    >>> rcfg = SEAScope.lib.utils.create_rendering_config(533, 5)
    >>> print(rcfg)
    {'rendered': True,
     'logscale': False,
     'min': 0,
     'max': 1,
     'opacity': 1.0,
     'zindex': 500,
     'color': [50, 12, 87],
     'colormap': 'grayscale',
     'renderMethod': 'RASTER',
     'particlesCount': 1000,
     'particleTTL': 10,
     'streamlineLength': 20,
     'streamlineSpeed': 0.0,
     'filterMode': 'NEAREST',
     'billboardsSize': 32,
     'billboardsDensity': 0,
     'lineThickness': 1,
     'target': {'granuleLevel': False,
                'sourceId': 1,
                'collectionId': 533,
                'granuleId': 0,
                'variableId': 5}}
    """
    target = {'granuleLevel': False,
              'sourceId': 1,
              'collectionId': col_id,
              'granuleId': 0,
              'variableId': var_id}

    result = {'rendered': True,
              'logscale': False,
              'min': 0,
              'max': 1,
              'opacity': 1.0,
              'zindex': 500,
              'color': [50, 12, 87],
              'colormap': 'grayscale',
              'renderMethod': 'RASTER',
              'particlesCount': 1000,
              'particleTTL': 10,
              'streamlineLength': 20,
              'streamlineSpeed': 0.0,
              'filterMode': 'NEAREST',
              'billboardsSize': 32,
              'billboardsDensity': 0,
              'lineThickness': 1,
              'target': target}
    return result


def create_granule(collection_id, gcps, start, stop):
    """Helper method to create the dictionary that represents a granule.

    Most fields are initialized with default values that you can/should
    customize before passing the generated dictionary to other methods.

    Time coverage is [start, stop[

    Parameters
    ----------
    collection_id : int
        Local (i.e. specifc to the current data source) identifier for the
        collection of the granule
    gcps : list of dict
        List of Ground Control Points, represented as dictionaries with four
        keys: lon, lat, i and j, that give the spatial coverage of the
        granule and provide intermediary points to map data on a sphere
    start : datetime.datetime
        Begining of the time coverage of the granule, in UTC (included)
    stop : datetime.datetime
        End of the time coverage of the granule, in UTC (excluded)

    Returns
    -------
    tuple(int, dict)
        A tuple which contains two elements:

          - an integer which is the local identifier, i.e. the identifier
            within a source, for the granule

          - a dictionary which contains all the information SEAScope needs to
            identify and format data associated with the granule.
    """
    granule_id = next(granule_id_generator)
    _start = (start - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    _stop = (stop - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    data_id = 'user_generated_granule_{}'.format(granule_id)
    shape_arity = math.sqrt(len(gcps))
    shape = {'xArity': shape_arity,
             'yArity': shape_arity,
             'gcps': gcps}
    idf = {'uri': 'Python: {}'.format(data_id),
           'xArity': 0,
           'yArity': 0,
           'resolution': 1000000000,
           'subsampling_factor': 0,
           'shape': shape}
    metadata = {'sourceId': 1,
                'collectionId': collection_id,
                'granuleId': granule_id,
                'dataId': data_id,
                'dataModel': None,
                'start': int(_start),
                'stop': int(_stop),
                'uris': [idf],
                'title': data_id,
                'institution': '',
                'comment': '',
                'file_id': idf['uri'],
                'product_version': '0.0.0',
                'lat_min': min([gcp['lat'] for gcp in gcps]),
                'lat_max': max([gcp['lat'] for gcp in gcps]),
                'lon_min': min([gcp['lon'] for gcp in gcps]),
                'lon_max': max([gcp['lon'] for gcp in gcps]),
                'creator_email': '',
                'station_id': '',
                'platform': '',
                'sensor': ''}
    granule = {'id': {'granuleLevel': True,
                      'sourceId': 1,
                      'collectionId': collection_id,
                      'granuleId': granule_id,
                      'variableId': 0},
               'metadata': metadata,
               'data': {}}

    return (granule_id, granule)


def set_field(granule, field_name, field_data, dynamic_packing=True,
              as_float=False):
    """Attach data to a granule

    Parameters
    ----------
    granule : dict
        Dictionary that represents a granule, such as the output of
        :func:`SEAScope.lib.utils.create_granule`
    field_name : str
        Name that will identify the data within the granule. Please note that
        granules that belong to the same collection must *all* have the same
        fields
    field_data : numpy.ndarray or numpy.ma.MaskedArray
        Data that must be attached to the granule
    dynamic_packing : bool, optional
        If False the values contained in ``field_data`` will be included "as
        is", otherwise (default behavior) the min and max values of
        ``field_data`` are used to project the data in the ubyte domain: min
        value is mapped to 0, max value to 254 and intermediary values are
        interpolated. 255 is used to represent masked data.
    as_float : bool, optional
        If True data are converted to float32 values, otherwise they are
        converted to unsigned bytes (default behavior).

    Raises
    ------
    DynamicPackingFloatIncompatbilityError
        Raised when ``dynamic_packing`` and ``as_float`` are both True because
        dynamic packing is only implemented for unsigned bytes
    FieldShapeError
        Raised when ``field_data`` is neither 1D nor 2D
    IncompatibleFieldError
        Raised when a field cannot be added to a granule because it is not
        compatible with already attached fields (shape mismatch)
    """
    if (dynamic_packing is True) and (as_float is True):
        raise DynamicPackingFloatIncompatbilityError()

    import numpy
    x_arity = 0
    y_arity = 0
    shape = numpy.shape(field_data)
    dims = len(shape)
    if 1 == dims:
        x_arity = shape[0]
        y_arity = 1
    elif 2 == dims:
        # Invert x and y since 2D data is transposed
        x_arity = shape[1]
        y_arity = shape[0]
    else:
        raise FieldShapeError('Field data must be either 1D or 2D')

    if granule['metadata']['dataModel'] is None:
        if 1 == dims:
            granule['metadata']['dataModel'] = 'TIME'
            granule['metadata']['uris'][0]['shape']['xArity'] = x_arity
            granule['metadata']['uris'][0]['shape']['yArity'] = 1
        elif 2 == dims:
            granule['metadata']['dataModel'] = 'ROW_CELL'
        granule['metadata']['uris'][0]['xArity'] = x_arity
        granule['metadata']['uris'][0]['yArity'] = y_arity

    # Check compatibility between field and granule geometries
    if (2 == dims) and ('TIME' == granule['metadata']['dataModel']):
        raise IncompatibleFieldError('Adding a 2D field on a granule which '
                                     'already contains a 1D field is not '
                                     'supported')
    elif (1 == dims) and ('TIME' != granule['metadata']['dataModel']):
        raise IncompatibleFieldError('Adding a 1D field on a granule which '
                                     'already contains a 2D field is not '
                                     'supported')

    ref_x_arity = granule['metadata']['uris'][0]['xArity']
    ref_y_arity = granule['metadata']['uris'][0]['yArity']
    if (x_arity != ref_x_arity) or (y_arity != ref_y_arity):
        field_shape = '{}x{}'.format(x_arity, y_arity)
        ref_shape = '{}x{}'.format(ref_x_arity, ref_y_arity)
        raise IncompatibleFieldError('All fields must have the same shape '
                                     'within a granule: you can not add a '
                                     'field with a {} shape in a granule which'
                                     ' contains {} fields'.format(field_shape,
                                                                  ref_shape))

    # Find packing parameters
    offset = 0.0
    scale = 1.0
    if dynamic_packing:
        vmin = numpy.nanmin(field_data)
        vmax = numpy.nanmax(field_data)
        offset = vmin
        scale = (vmax - vmin) / 254
        if vmin == vmax:
            scale = 1.0

    # Data must be flipped and transposed for SEAScope
    if 2 == dims:
        transposed = numpy.transpose(field_data.copy())
    else:
        transposed = field_data

    transposed_masked = numpy.ma.masked_invalid(transposed)
    transposed_mask = numpy.ma.getmaskarray(transposed_masked)
    mask_ind = numpy.where(transposed_mask)

    if as_float is False:
        # Pack data as uint8 (max value <=> 254, 255 is reserved for mask)
        transposed[mask_ind] = 0
        data_packed = (transposed - offset) / scale
        data_clipped = numpy.clip(data_packed, 0, 254).astype('uint8')

        # Mask invalid values (255 is used as fill value)
        fill_value = 255
        if numpy.any(transposed_mask):
            data_clipped[mask_ind] = fill_value

        data_type = 'uint8'
    else:
        transposed[mask_ind] = 0.0
        data_packed = (transposed - offset) / scale
        data_clipped = data_packed.astype('f4')

        # Mask invalid values using netCDF4 default fill value for float32
        fill_value = float.fromhex('0x1.e000000000000p+122')
        if numpy.any(transposed_mask):
            data_clipped[mask_ind] = fill_value

        data_type = 'float32'

    # Data must be stored as a 1D array (required for serialization)
    data_flattened = data_clipped.flatten('F')  # .tolist()

    channels = 1
    info = {'channels': channels,
            'xArity': x_arity,
            'yArity': y_arity,
            'dataType': data_type,
            'offsets': [offset],
            'scaleFactors': [scale],
            'fillValues': [fill_value]}

    granule['data'][field_name] = {'info': info,
                                   'buffer': data_flattened}


def get_lonlat(extraction, shape):
    """Rebuild lon/lat grids at an arbitrary resolution using interpolation,
    based on the GCPs provided by SEAScope extracted data.

    Parameters
    ----------
    extraction : dict
        Extraction from a single granule, deserialized and reformatted. This is
        usually *one* item of dictionary returned by
        :func:`SEAScope.lib.get_extracted_data`
    shape : tuple
        Shape of the resulting lon/lat grids

    Returns
    -------
    tuple(numpy.ndarray, numpy.ndarray)
        A tuple which contains two elements:

        - a grid of interpolated longitudes for the spatial covergae of the
          extraction

        - a grid of interpolated latitudes for the spatial coverage of the
          extraction

    Raises
    ------
    InvalidShapeError
        Error raised when the ``shape`` passed as parameter does not match a
        2D matrix

    Example
    -------
    >>> import SEAScope.lib
    >>> import SEAScope.lib.utils
    >>> extraction = SEAScope.lib.get_extracted_data('127.0.0.1', 11155)
    >>> print([str(x) for x in extraction.keys()])
    ['/seascope/data/ecmwf/ECMWF_20151201T12Z/ECMWF_20151201T12Z_idf_00.nc']
    >>> lons, lats = SEAScope.lib.utils.get_lonlat(extraction['/seascope/data/ecmwf/ECMWF_20151201T12Z/ECMWF_20151201T12Z_idf_00.nc'], (1000,1000))  # noqa:E501
    """
    import numpy

    if 2 != len(shape):
        raise InvalidShapeError('The "shape" parameter must have exactly two '
                                'components.')

    gcps = extraction['meta']['gcps']
    i_gcp = numpy.array([_['i'] for _ in gcps])
    j_gcp = numpy.array([_['j'] for _ in gcps])
    lon_gcp = numpy.array([_['lon'] for _ in gcps])
    lat_gcp = numpy.array([_['lat'] for _ in gcps])

    # Enforce longitude continuity (to be improved)
    if (lon_gcp[-1] - lon_gcp[0]) > 180.0:
        logger.warn('Difference between first and last longitude exceeds '
                    '180 degrees, assuming IDL crossing and remapping '
                    'longitudes in [0, 360]')
        lon_gcp = numpy.mod((lon_gcp + 360.0), 360.0)

    # Restore shape of the GCPs
    gcps_shape = (8, 8)  # hardcoded in SEAScope
    i_shaped = numpy.reshape(i_gcp, gcps_shape)
    j_shaped = numpy.reshape(j_gcp, gcps_shape)
    lon_shaped = numpy.reshape(lon_gcp, gcps_shape)
    lat_shaped = numpy.reshape(lat_gcp, gcps_shape)

    dst_lin = numpy.arange(0, shape[0])
    dst_pix = numpy.arange(0, shape[1])
    _dst_lin = numpy.tile(dst_lin[:, numpy.newaxis], (1, shape[1]))
    _dst_pix = numpy.tile(dst_pix[numpy.newaxis, :], (shape[0], 1))

    lon_2D, lat_2D = geoloc_from_gcps(lon_shaped, lat_shaped, j_shaped,
                                      i_shaped, _dst_lin, _dst_pix)

    return lon_2D, lat_2D


def geoloc_from_gcps(gcplon, gcplat, gcplin, gcppix, lin, pix):
    """"""
    import numpy
    import pyproj
    geod = pyproj.Geod(ellps='WGS84')
    fwd, bwd, dis = geod.inv(gcplon[:, :-1], gcplat[:, :-1],
                             gcplon[:, 1:], gcplat[:, 1:])

    # Find line and column for the top-left corner of the 4x4 GCPs cell which
    # contains the requested locations
    nlin, npix = gcplat.shape
    _gcplin = gcplin[:, 0]
    _gcppix = gcppix[0, :]
    top_line = numpy.searchsorted(_gcplin, lin, side='right') - 1
    left_column = numpy.searchsorted(_gcppix, pix, side='right') - 1

    # Make sure this line and column remain within the matrix and that there
    # are adjacent line and column to define the bottom-right corner of the 4x4
    # GCPs cell
    top_line = numpy.clip(top_line, 0, nlin - 2)
    bottom_line = top_line + 1
    left_column = numpy.clip(left_column, 0, npix - 2)
    right_column = left_column + 1

    # Compute coordinates of the requested locations in the 4x4 GCPs cell
    line_extent = _gcplin[bottom_line] - _gcplin[top_line]
    column_extent = _gcppix[right_column] - _gcppix[left_column]
    line_rel_pos = (lin - _gcplin[top_line]) / line_extent
    column_rel_pos = (pix - _gcppix[left_column]) / column_extent

    # Compute geographical coordinates of the requested locations projected on
    # the top and bottom lines
    lon1, lat1, _ = geod.fwd(gcplon[top_line, left_column],
                             gcplat[top_line, left_column],
                             fwd[top_line, left_column],
                             dis[top_line, left_column] * column_rel_pos)
    lon2, lat2, _ = geod.fwd(gcplon[bottom_line, left_column],
                             gcplat[bottom_line, left_column],
                             fwd[bottom_line, left_column],
                             dis[bottom_line, left_column] * column_rel_pos)

    # Compute the geographical coordinates of the requested locations projected
    # on a virtual column joining the projected points on the top and bottom
    # lines
    fwd12, bwd12, dis12 = geod.inv(lon1, lat1, lon2, lat2)
    lon, lat, _ = geod.fwd(lon1, lat1, fwd12, dis12 * line_rel_pos)

    return lon, lat


def import_granule_from_syntool(data_path, wkt, col_id, start, stop, field):
    """Read data extracted as Numpy objects using Syntool and import them in
    SEAScope.

    Note that Syntool dialog that pops up once the extraction is ready not
    only contains download links to get the extracted data but also the
    shape of the extracted area. You *must* save the shape (displayed in WKT
    format) in order to use this method as it is used as spatial coverage for
    the granule.

    Parameters
    ----------
    data_path : string
        Path of the data extracted in Numpy format
    wkt : string
        Shape of the extracted data, expressed in WKT format
    col_id : int
        Local, i.e. specific to the current data source, identifier for the
        collection that the granule containing the imported data will be
        attached to
    start: datetime.datetime
        Begining of the time coverage of the granule, in UTC (included)
    stop : datetime.datetime
        End of the time coverage of the granule, in UTC (excluded)
    field : string
        Name of the field that the extracted data corresponds to

    Example
    -------
    >>> import SEAScope.lib.utils
    >>> import datetime
    >>> coll_id, coll_dict = SEAScope.lib.utils.create_collection('Syntool data')  # noqa:E501
    >>> npy_path = '/tmp/3857_REMSS_MWOI_SST_v05.0-20190527120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.0.npy'  # noqa:E501
    >>> shape_wkt = 'POLYGON((-42.3633 24.1267,-21.0938 24.1267,-21.0938 41.9677,-42.3633 41.9677,-42.3633 24.1267))'  # noqa:E501
    >>> start_dt = datetime.datetime(2019, 5, 27, 0, 0, 0)
    >>> stop_dt = datetime.datetime(2019, 5, 28, 0, 0, 0)
    >>> granule_id, granule_dict = SEAScope.lib.utils.import_granule_from_syntool(npy_path, shape_wkt, coll_id, start_dt, stop_dt, 'sst')  # noqa:E501
    >>> print(granule_id)
    1000
    >>> print(granule_dict)
    {'id': {'granuleLevel': True,
            'sourceId': 1,
            'collectionId': 11,
            'granuleId': 1000,
            'variableId': 0},
     'metadata': {'sourceId': 1,
                  'collectionId': 11,
                  'granuleId': 1000,
                  'dataId': 'user_generated_granule_1000',
                  'dataModel': 'ROW_CELL',
                  'start': 1558915200000,
                  'stop': 1559001600000,
                  'uris': [{'uri': 'Python: user_generated_granule_1000',
                            'xArity': 244,
                            'yArity': 242,
                            'resolution': 1000000000,
                            'subsampling_factor': 0,
                            'shape': {'xArity': 2.0,
                                      'yArity': 2.0,
                                      'gcps': [{'lon': -21.0938,
                                                'lat': 24.1267,
                                                'i': 243,
                                                'j': 241},
                                               {'lon': -42.3633,
                                                'lat': 24.1267,
                                                'i': 243,
                                                'j': 0},
                                               {'lon': -21.0938,
                                                'lat': 41.9677,
                                                'i': 0,
                                                'j': 241},
                                               {'lon': -42.3633,
                                                'lat': 41.9677,
                                                'i': 0,
                                                'j': 0}]}}],
                  'title': 'user_generated_granule_1000',
                  'institution': '',
                  'comment': '',
                  'file_id': 'Python: user_generated_granule_1000',
                  'product_version': '0.0.0',
                  'lat_min': 24.1267,
                  'lat_max': 41.9677,
                  'lon_min': -42.3633,
                  'lon_max': -21.0938,
                  'creator_email': '',
                  'station_id': '',
                  'platform': '',
                  'sensor': ''},
     'data': {'sst': {'info': {'channels': 1,
                               'xArity': 244,
                               'yArity': 242,
                               'dataType': 'uint8',
                               'offset': [0.0],
                               'scaleFactors': [1.0],
                               'fillValues': [255]},
                               'buffer': [...]}}}

    """
    import numpy
    data = numpy.load(data_path)
    data_transposed = numpy.ma.masked_values(numpy.transpose(data), 255)
    data_shape = numpy.shape(data_transposed)

    _wkt = wkt.strip()
    i0 = 1 + _wkt.rfind('(')
    i1 = _wkt.find(')')
    _vertices = [y.strip().split(' ') for y in _wkt[i0:i1].split(',')][:-1]
    vertices = [(float(x[0].strip()), float(x[1].strip())) for x in _vertices]

    # Build GCPs
    gcp0 = {'lon': vertices[1][0], 'lat': vertices[1][1],
            'i': data_shape[1] - 1, 'j': data_shape[0] - 1}
    gcp1 = {'lon': vertices[0][0], 'lat': vertices[0][1],
            'i': data_shape[1] - 1, 'j': 0}
    gcp2 = {'lon': vertices[2][0], 'lat': vertices[2][1],
            'i': 0, 'j': data_shape[0] - 1}
    gcp3 = {'lon': vertices[3][0], 'lat': vertices[3][1],
            'i': 0, 'j': 0}
    gcps = [gcp0, gcp1, gcp2, gcp3]

    granule_id, granule = create_granule(col_id, gcps, start, stop)
    set_field(granule, field, data_transposed, dynamic_packing=False)

    return (granule_id, granule)


def raw2data(raw_result):
    """Reformat raw data received from SEAScope, after it has been deserialized
    by FlatBuffers, into Numpy masked arrays.

    Parameters
    ----------
    raw_result : dict
        Deserialized version of the data received from SEAScope

    Returns
    -------
    dict
        Data received from SEAScope transformed into Numpy masked arrays
    """
    import numpy
    clean_data = {}
    for extraction in raw_result:
        uri = extraction['uri'].decode('utf-8')
        if uri not in clean_data:
            clean_data[uri] = {}
            shape = (extraction['yArity'], extraction['xArity'])
            clean_data[uri]['data'] = {}
            _start = datetime.datetime.utcfromtimestamp(extraction['start'])
            _stop = datetime.datetime.utcfromtimestamp(extraction['stop'])
            clean_data[uri]['meta'] = {"shape": shape,
                                       "gcps": extraction['gcps'],
                                       'fill_values': [],
                                       'fields': [],
                                       'start': _start,
                                       'stop': _stop}

        d = numpy.array(extraction['buffer'], dtype=numpy.float32)
        logger.debug('Full shape: {}'.format(d.shape))
        fill_values = extraction['fill_values']

        d0 = d[::4]
        data = [d0]

        if 1 < len(fill_values):
            d1 = d[1::4]
            data.append(d1)

        if 2 < len(fill_values):
            d2 = d[2::4]
            data.append(d2)

        is_mask = ((1 == len(data)) and (0 == len(extraction['fields'])) and
                   ('mask' == uri))
        for n in range(len(data)):
            if is_mask:
                field_name = 'mask'
                fill_value = 0
            else:
                field_name = (extraction['fields'][n]).decode('utf-8')
                fill_value = extraction['fill_values'][n]
            if field_name in clean_data[uri]['data']:
                # Field values already extracted from another variable
                continue
            dn_reshaped = numpy.reshape(data[n], shape)
            dn_masked = numpy.ma.masked_values(dn_reshaped, fill_value)
            dn_clean = numpy.ma.masked_invalid(dn_masked)
            clean_data[uri]['data'][field_name] = dn_clean
            clean_data[uri]['meta']['fill_values'].append(fill_value)
            clean_data[uri]['meta']['fields'].append(field_name)

    logger.info(' .:| Available granules |:.')
    logger.info(' --------------------------')
    for k in clean_data.keys():
        logger.info('• {}'.format(k))

    return clean_data
