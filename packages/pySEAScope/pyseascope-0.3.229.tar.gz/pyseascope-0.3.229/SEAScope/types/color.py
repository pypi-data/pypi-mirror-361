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
This module handles the serialization and deserialization of color values
"""

import logging
import flatbuffers
import SEAScope.API.Color

logger = logging.getLogger(__name__)


def serialize(builder, color_obj):
    """
    Serialize a rendering configuration using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    color_obj : :obj:`list` of 3 :obj:`int`
        The color described by its red, green and blue channels

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

    cls = SEAScope.API.Color
    color = cls.CreateColor(builder,
                            int(color_obj[0]),
                            int(color_obj[1]),
                            int(color_obj[2]))

    return builder, color


def deserialize(o):
    """
    Rebuild a color from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the color object serialized with FlatBuffers

    Returns
    -------
    dict
        The deserialized color object as a :obj:`list` of 3 :obj:`int` (R, G
        and B)
    """
    result = []
    result.append(o.R())
    result.append(o.G())
    result.append(o.B())
    return result
