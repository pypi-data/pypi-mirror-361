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
This module handles the serialization and deserialization of shape objects
"""

import logging
import flatbuffers
import SEAScope.API.Shape
import SEAScope.types.gcp

logger = logging.getLogger(__name__)


def serialize(builder, shp_obj):
    """
    Serialize a shape using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    shp_obj : dict
        Dictionary which contains information about the shape to serialize
        It must have three keys:

        - ``xArity`` : an :obj:`int` which tells SEAScope how many columns it
          must allocate when reconstructing the GCPs matrix

        - ``yArity`` : an :obj:`int` which tells SEAScope how many rows it
          must allocate when reconstructing the GCPs matrix

        - ``gcps`` : a :obj:`list` of :obj:`dict` containing information
          about the GCPs of the shape.
          Each :obj:`dict` object must have all the keys required by
          :func:`SEAScope.types.gcp.serialize`

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

    x_arity = int(shp_obj['xArity'])
    y_arity = int(shp_obj['yArity'])
    gcps_len = len(shp_obj['gcps'])
    SEAScope.API.Shape.ShapeStartGcpsVector(builder, gcps_len)
    for gcp in shp_obj['gcps'][::-1]:
        _, _gcp = SEAScope.types.gcp.serialize(builder, gcp)
    gcps = builder.EndVector(gcps_len)

    cls = SEAScope.API.Shape
    cls.ShapeStart(builder)
    cls.ShapeAddXArity(builder, x_arity)
    cls.ShapeAddYArity(builder, y_arity)
    cls.ShapeAddGcps(builder, gcps)
    shape = cls.ShapeEnd(builder)
    return builder, shape


def deserialize(o):
    """
    Rebuild a shape from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the shape object serialized with FlatBuffers

    Returns
    -------
    dict
        The deserialized shape object as a dictionary.
    """
    deserializer = SEAScope.types.gcp.deserialize
    s_obj = {}
    s_obj['xArity'] = o.XArity()
    s_obj['yArity'] = o.YArity()
    gcps_count = o.GcpsLength()
    s_obj['gcps'] = [deserializer(o.Gcps(x)) for x in range(0, gcps_count)]

    return s_obj
