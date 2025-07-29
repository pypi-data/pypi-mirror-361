# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-09
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
This module handles the serialization and deserialization of GCP objects
"""

import logging
import flatbuffers
import SEAScope.API.GCP

logger = logging.getLogger(__name__)


def serialize(builder, gcp_obj):
    """
    Serialize a GCP using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    gcp_obj : dict
        Dictionary which contains information about the GCP to serialize

        It must have four keys:

        - ``lon`` : a :obj:`float` which gives the longitude of the GCP

        - ``lat`` : a :obj:`float` which gives the latitude of the GCP

        - ``i`` : an :obj:`int` which is the number of the column in the data
          matrix for the GCP

        - ``j`` : an :obj:`int` which is the number of the row in the data
          matrix for the GCP

        There is a fifth optional key:

        - ``time`` : a :obj:`int` which is the number of milliseconds since
          epoch for the GCP. The default value is 0 if this key is not
          provided.

    Returns
    -------
    tuple(flatbuffers.builder.Builder, int)
        A tuple which contains two elements:

        - the :obj:`flatbuffers.builder.Builder` instance which has been used
          to serialize data
        - an :obj:`int` which is the address/offset of the serialized object
          in the builder buffer
    """
    if builder is None:
        builder = flatbuffers.Builder(0)

    time_value = gcp_obj.get('time', 0)
    cls = SEAScope.API.GCP
    gcp = cls.CreateGCP(builder,
                        time_value,
                        gcp_obj['lon'],
                        gcp_obj['lat'],
                        int(gcp_obj['i']),
                        int(gcp_obj['j']))

    return builder, gcp


def deserialize(o):
    """
    Rebuild a GCP from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contain the GCP object serialized with FlatBuffers

    Returns
    -------
    dict
        The deserialized GCP object as a dictionary.
    """
    result = {}
    result['time'] = o.Time()
    result['lon'] = o.Lon()
    result['lat'] = o.Lat()
    result['i'] = o.I()
    result['j'] = o.J()
    return result
