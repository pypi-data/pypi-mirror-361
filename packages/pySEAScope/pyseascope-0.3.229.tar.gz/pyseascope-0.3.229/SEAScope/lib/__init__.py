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
This module provides some helper methods required by the seascope-processor
command to process data extracted by SEAScope.
"""

import struct
import numpy
import logging

import SEAScope.cmds.get_extraction
import SEAScope.lib.utils
import SEAScope.upload
try:
    import cPickle as pickle
except ImportError:
    import pickle

logger = logging.getLogger(__name__)


def get_dists(mask):
    """Compute the cumulative distance between a list of locations provided
    by SEAScope when the user makes a transect.

    Parameters
    ----------
    mask : dict
        Data structure (similar to granules) created by SEAscope when the user
        extracts data along a polyline (transect)

    Returns
    -------
    list of float
        The cumulative distances covered at each point while following the
        transect, in kilometers
    """
    import pyproj
    geod = pyproj.Geod(ellps='WGS84')
    gcps = mask['meta']['gcps']

    dists = [0.0]
    last_lon = gcps[0]['lon']
    last_lat = gcps[0]['lat']
    logger.debug('Number of steps: {}'.format(len(gcps)))

    for n in range(1, len(gcps)):
        lon = gcps[n]['lon']
        lat = gcps[n]['lat']
        _, _, d = geod.inv(last_lon, last_lat, lon, lat)
        dists.append(dists[-1] + .001 * d)
        last_lon = lon
        last_lat = lat

    return dists


def _arrays2rgb(channels):
    """Deprecated?"""
    ubyte_data = []
    for n in range(0, 3):
        d_min = numpy.min(channels[n])
        d_max = numpy.max(channels[n])
        extent = d_min - d_max
        if d_min == d_max:
            extent = 1.0
        d_ubyte = 255 * (channels[n] - d_min) / extent
        ubyte_data.append(d_ubyte)
    rgb = numpy.stack(ubyte_data, axis=2).astype(numpy.ubyte)
    return rgb


def _read_response(link, msg_size):
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
    already_read = 0
    result = b''
    while already_read < msg_size:
        buf = link.recv(chunk_size)
        already_read += len(buf)
        result += buf
        chunk_size = msg_size - already_read

    return result


def get_extracted_data(host='localhost', port=11155):
    """Fetch extracted data from SEAScope and format the result to make it
    easier to manipulate.

    Parameters
    ----------
    host : str
        IP address of the network interface that the SEAScope application
        listens to.
    port : int
        Port number that the SEAScope application listens to.

    Returns
    -------
    dict
        The data extracted by SEAScope, reformatted to be easier to analyse and
        manipulate
    """
    logger.info('Retrieving extracted data...')
    with SEAScope.upload.connect(host, port) as s:
        serializer = SEAScope.cmds.get_extraction.serialize
        builder = None
        builder, serialized = serializer(builder)
        builder.Finish(serialized)
        buf = builder.Output()
        s.sendall(struct.pack('>Q', len(buf))+buf)

        buf = s.recv(8)
        msg_len = struct.unpack('<Q', buf)
        logger.debug('Read {} bytes'.format(msg_len[0]))
        buf = _read_response(s, msg_len[0])
        logger.debug('{} bytes read'.format(len(buf)))
        deserializer = SEAScope.cmds.get_extraction.deserialize
        raw_result = deserializer(buf)

    clean_data = SEAScope.lib.utils.raw2data(raw_result)
    del raw_result
    return clean_data


def save_pyo(obj, output_path):
    """Serialize a Python object and save the result on the filesystem.

    Parameters
    ----------
    obj : `object`
        A serializable Python object
    output_path : str
        Path of the file that will contain the serialized object
    """
    with open(output_path, 'wb') as f:
        pickle.dump(obj, f, protocol=1)


def load_pyo(input_path):
    """Load a file from the filesystem and deserialize its content as a Python
    object.

    Parameters
    ----------
    input_path : str
        Path of the file which contains a serialized Python object

    Returns
    -------
    object
        The deserialized Python object
    """
    obj = None
    with open(input_path, 'rb') as f:
        obj = pickle.load(f)
    return obj
