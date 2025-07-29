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

"""This module provides helpers methods to interact with the SEAScope
application.
"""

import sys
import time
import struct
import socket
import logging
import calendar
import datetime
import contextlib
import SEAScope.cmds.add_collection
import SEAScope.cmds.add_variable
import SEAScope.cmds.add_granule
import SEAScope.cmds.set_rendering
import SEAScope.cmds.get_rendering
import SEAScope.cmds.set_current_datetime
import SEAScope.cmds.set_altitude
import SEAScope.cmds.look_at
import SEAScope.cmds.zoom_in
import SEAScope.cmds.zoom_out
import SEAScope.cmds.reset_camera
import SEAScope.cmds.select_variable
import SEAScope.cmds.select_variable_by_label
import SEAScope.cmds.get_variable_identifier
import SEAScope.cmds.check_schema_version

logger = logging.getLogger(__name__)


class CollectionIdConflict(Exception):
    """Execption raised when a collection creation request fails because the
    collection identifier is already used by a collection registered in
    SEAScope"""
    pass


class Throttler(object):
    """Timer that provides a throttling mechanism."""

    def __init__(self):
        self.__last_upload = 0
        self.__min_delay_ms = 0

    @property
    def min_delay(self):
        """int: Minimal delay between two successive calls to
        :func:`SEAScope.upload.Throttler.apply_delay`, in milliseconds"""
        return self.__min_delay_ms

    @min_delay.setter
    def min_delay(self, value):
        logger.debug('Set min delay to {}'.format(value))
        self.__min_delay_ms = max(0, value)

    def apply_delay(self):
        """Wait until the minimal delay since last call has been reached."""
        now = datetime.datetime.utcnow()
        now_ms = time.mktime(now.timetuple()) * 1e3 + now.microsecond / 1e3
        elapsed = now_ms - self.__last_upload
        if elapsed < self.__min_delay_ms:
            to_wait_ms = self.__min_delay_ms - elapsed
            logger.debug('Delay for {}ms'.format(to_wait_ms))
            time.sleep(to_wait_ms / 1e3)
            now = datetime.datetime.utcnow()
            now_ms = time.mktime(now.timetuple()) * 1e3 + now.microsecond / 1e3
        self.__last_upload = now_ms


throttler = Throttler()
"""`SEAScope.upload.Throttler`: Global throttler object that is shared by all
the methods provided in :mod:`SEAScope.upload`. Use it to set the minimal
delay between two API calls if SEAScope is not able to handle the number of
requests sent by Python in a short period of time."""


@contextlib.contextmanager
def connect(host, port, check_schema_version=False):
    """Create a socket and connect it to the SEAScope application which listens
    on the provided IP address and port.

    Parameters
    ----------
    host : str
        IP address of the network interface that the SEAScope application
        listens to.
    port : int
        Port number that the SEAScope application listens to.

    Returns
    -------
    socket.socket
        a socket connected to SEAScope

    Example
    -------
    >>> import SEAScope.upload
    >>> with SEAScope.upload.connect('192.168.1.32', 5555) as link:
    >>>     # Pass the link object to other method so that they can communicate
    >>>     # with SEAScope
    >>>     # [...]
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        if check_schema_version is True:
            _check_schema_version(s)

        yield s
    except:  # noqa
        _, e, _ = sys.exc_info()
        logger.error(e)
        raise
    finally:
        logger.debug('Closing connection')
        s.send(b'')
        s.shutdown(socket.SHUT_RDWR)
        s.close()


def _check_schema_version(link) -> None:
    """Compare data serialization schema versions used by the SEAScope client
    and by this package. Issue a warning in case they do not match because
    extracting objects from a binary stream using the wrong data schema could
    lead to unpredictable errors and crashes.

    Parameters
    ----------
    link: socket.socket
        Stream socket connected to SEAScope
    """
    # Request rendering config from SEAScope
    serializer = SEAScope.cmds.check_schema_version.serialize
    builder = None
    builder, serialized = serializer(builder)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)

    # Retrieve result
    deserializer = SEAScope.cmds.check_schema_version.deserialize

    # SEAScope versions that do not implement the checkSchemaVersion command
    # will not return anything. The command should execute very fast, so if
    # there is no response within one second it is reasonable to conclude that
    # the SEAScope client does not support this function and therefore uses
    # an old schema version
    timeout = link.gettimeout()
    link.settimeout(1.0)
    try:
        buf = link.recv(8)
    except TimeoutError:
        logger.warning('The SEAScope viewer uses an old version of the data '
                       'serialization schema compared to the one built in this'
                       ' Python package.\n'
                       'Although some commands might work, using mismatching '
                       'schema versions may lead to errors or even crashes.\n'
                       'Please use a more recent SEAScope viewer or install '
                       'the SEAScope Python package released around the same '
                       'time as the viewer to get the best compatibility '
                       'between Python and SEAScope')
        return
    finally:
        # Restore original timeout
        link.settimeout(timeout)

    msg_len = struct.unpack('<Q', buf)
    buf = read_response(link, msg_len[0])
    result = deserializer(buf)
    version_match, recommended_python_version = result
    if version_match is False:
        logger.warning('The SEAScope Python package does not use the same '
                       'data serialization schema as the SEAScope viewer.\n'
                       'Although some commands might work, using mismatching '
                       'schema versions may lead to errors or even crashes.\n'
                       'Please install SEAScope Python package version '
                       f'"{recommended_python_version}" to get the best '
                       'compatibility between Python and SEAScope.')


def read_response(link, msg_size):
    """Fetch a fixed number of bytes from the socket connected to SEAScope.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    msg_size : int
        Number of bytes to fetch from the socket

    Returns
    -------
    :obj:`list` of :obj:`bytes`
        Raw data sent by SEAScope"""
    chunk_size = msg_size
    logger.debug('Message size: {}'.format(msg_size))
    already_read = 0
    result = b''
    while already_read < msg_size:
        buf = link.recv(chunk_size)
        already_read += len(buf)
        result += buf
        chunk_size = msg_size - already_read
    return result


def collection(link, _collection):
    """Add a collection to SEAScope catalogue.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    _collection : dict
        Dictionary representing the collection


    Raises
    ------
    CollectionIdConflict
        Raised when the numerical identifier of the collection passed in the
        ``_collection`` parameter matches a collection already registered in
        SEAScope.

    Example
    -------
    >>> import SEAScope.upload
    >>> import SEAScope.lib.utils
    >>> coll_id, coll_obj = SEAScope.lib.utils.create_collection('Dummy')
    >>> print(coll_obj)
    {'id': {'granuleLevel': False,
            'sourceId': 1,
            'collectionId': 10,
            'granuleId': 0,
            'variableId': 0},
     'mustBeCurrent': False,
     'xSeamless': False,
     'ySeamless': False,
     'NEWSAligned': False,
     'label': 'Dummy',
     'tags': {},
     'variables': [],
     'variablesList': {},
     'defaultVariable': 0}
    >>> # Edit coll_obj to customize the collection
    >>> # [...]
    >>> with SEAScope.upload.connect(host, port) as link:
    >>>     SEAScope.upload.collection(link, coll_obj)
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.add_collection.serialize
    builder = None
    builder, serialized = serializer(builder, _collection)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)

    # Retrieve result
    deserializer = SEAScope.cmds.add_collection.deserialize
    buf = link.recv(8)
    msg_len = struct.unpack('<Q', buf)
    buf = read_response(link, msg_len[0])
    result = deserializer(buf)
    if result['ok'] is False:
        logger.error(f'Failed to add collection in SEAScope: {result["msg"]}')
        raise CollectionIdConflict


def variable(link, _variable):
    """Add a variable to SEAScope catalogue.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    _variable : dict
        Dictionary representing the variable

    Example
    -------
    >>> import SEAScope.upload
    >>> import SEAScope.lib.utils
    >>> collid, coll_obj = SEAScope.lib.create_collection('My collection')
    >>> var_obj = SEAScope.lib.create_variable(coll_obj, 'My variable',
    >>>                                        ['fieldA', 'fieldB'])
    >>> print(var_obj)
    {'id': 0,
     'label': 'My variable',
     'units': '',
     'fields': ['fieldA', 'fieldB'],
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
    >>> # You can customize the rendering configuration for the created
    >>> # variable by altering the content of var_obj['rendering']
    >>> # [...]
    >>> with SEAScope.upload.connect('127.0.0.1', 11155) as link:
    >>>     SEAScope.upload.collection(link, coll_obj)
    >>>     SEAScope.upload.variable(link, var_obj)
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.add_variable.serialize
    builder = None
    collection_id = _variable['collection']
    builder, serialized = serializer(builder, collection_id, _variable)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)

    # Retrieve result
    deserializer = SEAScope.cmds.add_variable.deserialize
    buf = link.recv(8)
    msg_len = struct.unpack('<Q', buf)
    buf = read_response(link, msg_len[0])
    result = deserializer(buf)
    if result['ok'] is False:
        logger.error(f'Failed to add variable in SEAScope: {result["msg"]}')

    if 'rendering' in _variable:
        rendering_config(link, _variable['rendering'])


def rendering_config(link, rcfg):
    """Update a rendering configuration

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    rcfg : dict
        Dictionary representing the rendering configuration

    Example
    -------
    >>> import SEAScope.upload
    >>> rcfg = {'rendered': True,
    >>>         'logscale': False,
    >>>         'min': 0.0,
    >>>         'max': 1.5,
    >>>         'opacity': 0.7,
    >>>         'zindex': 0.25,
    >>>         'color': [0, 0, 0],
    >>>         'colormap': 'jet',
    >>>         'renderMethod': 'RASTER',
    >>>         'filterMode': 'BILINEAR',
    >>>         'particlesCount': 0,
    >>>         'particleTTL': 0,
    >>>         'streamlineLength': 0,
    >>>         'streamlineSpeed': 0.0,
    >>>         'target': None}
    >>> with SEAScope.upload.connect('127.0.0.1', 11155) as link:
    >>>     target = SEAScope.upload.get_id_for(link, 'My collection',
    >>>                                         'My variable')
    >>>     # Update target in the rendering configuration dictionary
    >>>     rcfg['target'] = target
    >>>     SEAScope.upload.rendering_config(link, rcfg)
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.set_rendering.serialize
    builder = None
    builder, serialized = serializer(builder, rcfg)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)


def granule(link, _granule):
    """Add a granule in SEAScope.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    _granule : dict
        Dictionary representing the granule

    Example
    -------
    >>> import datetime
    >>> import SEAScope.upload
    >>> import SEAScope.lib.utils
    >>> # Example with 1D data: the GCPs will be the trajectory positions
    >>> lons = [1, 2, 3, 4, 5]  # dummy longitudes for the sake of example
    >>> lats = [|, 2, 3, 4, 5]  # dummy latitudes for the sake of example
    >>> gcps = [{'lon': lons[i], 'lat': lats[i], 'i': i, 'j': 0}
    >>>         for i in range(0, len(lons))]
    >>> # Define the time coverage of the granule
    >>> start = datetime.datetime(2019, 5, 21)
    >>> stop = datetime.datetime(2019, 5, 22, 14, 18, 56)
    >>> # Create a collection
    >>> coll_id, coll_obj = SEAScope.lib.utils.create_collection('My data')
    >>> # Create the granule object
    >>> gra_id, gra_obj = SEAScope.lib.utils.create_granule(coll_id, gcps,
    >>>                                                     start, stop)
    >>> # Associate some data with the granule
    >>> values = [31, 32, 33, 34, 35]  # replace this by actual measurements
    >>> SEAScope.lib.utils.set_field(gra_obj, 'field_name', values)
    >>> print(gra_obj)
    {'id': {'granuleLevel': True,
            'sourceId': 1,
            'collectionId': 10,
            'granuleId': 1000,
            'variableId': 0},
     'metadata': {'sourceId': 1,
                  'collectionId': 10,
                  'granuleId': 1000,
                  'dataId': 'user_generated_granule_1000',
                  'dataModel': 'TIME',
                  'start': 1558396800000,
                  'stop': 1558534736000,
                  'uris': [{'uri': 'Python: user_generated_granule_1000',
                            'xArity': 5,
                            'yArity': 2,
                            'resolution': 1000000000,
                            'subsampling_factor': 0,
                            'shape': {'xArity': 5,
                                      'yArity': 1,
                                      'gcps': [{'lon': 1, 'lat': 1, 'i': 0, 'j': 0},  # noqa:E501
                                               {'lon': 2, 'lat': 2, 'i': 1, 'j': 0},  # noqa:E501
                                               {'lon': 3, 'lat': 3, 'i': 2, 'j': 0},  # noqa:E501
                                               {'lon': 4, 'lat': 4, 'i': 3, 'j': 0},  # noqa:E501
                                               {'lon': 5, 'lat': 5, 'i': 4, 'j': 0}]}}],  # noqa:E501
                  'title': 'user_generated_granule_1000',
                  'institution': '',
                  'comment': '',
                  'file_id': 'Python: user_generated_granule_1000',
                  'product_version': '0.0.0',
                  'lat_min': 1,
                  'lat_max': 5,
                  'lon_min': 1,
                  'lon_max': 5,
                  'creator_email': '',
                  'station_id': '',
                  'platform': '',
                  'sensor': ''},
     'data': {'field_name': {'info': {'channels': 1,
                                      'xArity': 5,
                                      'yArity': 2,
                                      'dataType': 'uint8',
                                      'offsets': [31],
                             'scaleFactors': [0.015748031496062992],
                             'fillValues': [255]},
                             'buffer': [254, 190, 127, 63, 0]}}}
    >>> # Send everything to SEAScope
    >>> with SEAScope.upload.connect('127.0.0.1', 11155) as link:
    >>>     # Create the collection first!
    >>>     SEAScope.upload.collection(link, coll_obj)
    >>>     # Then the granule
    >>>     SEAScope.upload.granule(link, gra_obj)

    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.add_granule.serialize
    builder = None
    builder, serialized = serializer(builder, _granule)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)


def current_datetime(link, dt):
    """Set current datetime in SEAScope.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    dt : datetime.datetime
        Value that will be used as current datetime
    """
    global throttler
    throttler.apply_delay()

    timestamp = calendar.timegm(dt.timetuple())
    serializer = SEAScope.cmds.set_current_datetime.serialize
    builder = None
    builder, serialized = serializer(builder, timestamp)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf)) + buf)


def rendering_config_for(link, target):
    """Get the current rendering configuration for a (collection, variable)
    couple.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    target : dict
        Dictionary which contains the numerical identifiers for the target

    Returns
    -------
    dict
        Dictionary representing the rendering configuration

    Example
    -------
    >>> import SEASope.upload
    >>> with SEAScope.upload.connect('127.0.0.1', 11155) as link:
    >>>     target = SEAScope.upload.get_id_for(link, 'AVISO altimetry',
    >>>                                         'Mean Dynamic Topography')
    >>>     rcfg = SEAScope.upload.rendering_config_for(link, target)
    >>> print(rcfg)
    {'rendered': True,
     'logscale': False,
     'min': -0.30000001192092896,
     'max': 1.5,
     'opacity': 0.8999999761581421,
     'zindex': 0.22220000624656677,
     'color': [0, 0, 0],
     'colormap': b'jet',
     'renderMethod': 'RASTER',
     'filterMode': 'BILINEAR',
     'particlesCount': 0,
     'particleTTL': 0,
     'streamlineLength': 0,
     'streamlineSpeed': 0.0,
     'target': {'granuleLevel': False,
                'sourceId': 2,
                'collectionId': 11,
                'granuleId': 0,
                'variableId': 0}}
    """
    global throttler
    throttler.apply_delay()

    # Request rendering config from SEAScope
    serializer = SEAScope.cmds.get_rendering.serialize
    deserializer = SEAScope.cmds.get_rendering.deserialize
    builder = None
    builder, serialized = serializer(builder, target)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)

    # Retrieve result
    buf = link.recv(8)
    msg_len = struct.unpack('<Q', buf)
    buf = read_response(link, msg_len[0])
    result = deserializer(buf)
    return result


def altitude(link, altitude):
    """Set the altitude of the camera in SEAScope.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    altitude : float
        Distance between the ground and the camera, in meters
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.set_altitude.serialize
    builder = None
    builder, serialized = serializer(builder, altitude)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def location(link, lon, lat):
    """Set the location displayed at the center of the screen (the camera's
    target) in SEAScope.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    lon : float
        Longitude of the location
    lat : float
        Latitude of the location

    Notes
    -----
    The values passed to this method for longitudes and latitudes are wrapped
    automatically to match the domains that SEAScope can handle
    """
    global throttler
    throttler.apply_delay()

    lon = ((lon + 180.) % 360.) - 180.
    serializer = SEAScope.cmds.look_at.serialize
    builder = None
    builder, serialized = serializer(builder, lon, lat)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def zoom_in(link):
    """Zoom-in in SEAScope.
    The camera gets closer to the ground: camera altitude decreases by a
    distance that varies depending on the current altitude.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.zoom_in.serialize
    builder = None
    builder, serialized = serializer(builder)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def zoom_out(link):
    """Zoom-out in SEAScope.
    The camera goes further away from the ground: camera altitude increases by
    a distance that varies depending on the current altitude.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.zoom_out.serialize
    builder = None
    builder, serialized = serializer(builder)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def reset_camera(link):
    """Move camera back to its default position.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.reset_camera.serialize
    builder = None
    builder, serialized = serializer(builder)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def select_variable_by_id(link, source_id, collection_id, variable_id,
                          selected, exclusive):
    """Update the variables selection in SEAScope catalogue using numerical
    values to identify the target variable.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    source_id : int
        Numerical identifier for the data source for the collection
    collection_id : int
        Numerical identifier for the collection that contains the target
        variable
    variable_id:
        Numerical identifier for the target variable
    selected : bool
        New selection state for the variable (True = selected)
    exclusive : bool
        When set to True, this flag tells SEAScope to unselect all the
        variables that were previously selected (exclusive selection)
    """
    global throttler
    throttler.apply_delay()

    _rid = {'granuleLevel': False,
            'sourceId': source_id,
            'collectionId': collection_id,
            'granuleId': 0,
            'variableId': variable_id}

    serializer = SEAScope.cmds.select_variable.serialize
    builder = None
    builder, serialized = serializer(builder, _rid, selected, exclusive)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def select_variable_by_label(link, collection_label, variable_label, selected,
                             exclusive):
    """Update the variables selection in SEAScope catalogue using numerical
    values to identify the target variable.

    Parameters
    ----------
    link : socket.socket
        Stream socket connected to SEAScope
    collection_label : str
        Label of the collection that contains the target variable
    variable_label : str
        Label of the targt variable
    selected : bool
        New selection state for the variable (True = selected)
    exclusive : bool
        When set to True, this flag tells SEAScope to unselect all the
        variables that were previously selected (exclusive selection)
    """
    global throttler
    throttler.apply_delay()

    serializer = SEAScope.cmds.select_variable_by_label.serialize
    builder = None
    builder, serialized = serializer(builder, collection_label, variable_label,
                                     selected, exclusive)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)


def get_id_for(link, collection_label, variable_label):
    """Get the internal identifier which corresponds to a (collection,
    variable) couple using their labels (i.e. the text that describes them in
    the SEAScope catalogue menu).

    Parameters
    ----------
    link : socket
        Socket connected to the SEAScope application
    collection_label : str
        Label of the collection
    variable_label : str
        Label of the variable

    Returns
    -------
    dict
        Dictionary containing the numerical identifiers associated with the
        (collection, variable) couple

    Example
    -------
    >>> import SEAScope.upload
    >>> with SEAScope.upload.connect('127.0.0.1', 11155) as link:
    >>>     result = SEAScope.upload.get_id_for(link, 'ECMWF',
    >>>                                         'mean wind field')
    >>> print(result)
    {'granule_level': False,
     'sourceId': 2,
     'collectionId': 2,
     'granuleId': 0,
     'variableId': 0}
    """
    global throttler
    throttler.apply_delay()

    # Request rendering config from SEAScope
    serializer = SEAScope.cmds.get_variable_identifier.serialize
    deserializer = SEAScope.cmds.get_variable_identifier.deserialize
    builder = None
    builder, serialized = serializer(builder, collection_label, variable_label)
    builder.Finish(serialized)
    buf = builder.Output()
    link.sendall(struct.pack('>Q', len(buf))+buf)

    # Retrieve result
    buf = link.recv(8)
    msg_len = struct.unpack('<Q', buf)
    buf = read_response(link, msg_len[0])
    result = deserializer(buf)
    return result
