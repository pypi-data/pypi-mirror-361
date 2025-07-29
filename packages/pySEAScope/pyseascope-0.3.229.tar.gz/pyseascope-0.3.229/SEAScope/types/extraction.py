# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-10-20
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
This module handles the deserialization of extraction objects
"""

import flatbuffers
import SEAScope.types.renderable_id
import SEAScope.types.gcp

import struct
import logging
import flatbuffers.compat
import flatbuffers.number_types

logger = logging.getLogger(__name__)


def serialize(builder, obj):
    """
    Not implemented
    """
    pass


def deserialize(o):
    """
    Rebuild an extraction from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contain the extraction object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized extraction object as a dictionary.
    """
    result = {}
    result['id'] = SEAScope.types.renderable_id.deserialize(o.Id())
    result['xArity'] = o.XArity()
    result['yArity'] = o.YArity()
    result['channels'] = o.Channels()
    result['uri'] = o.Uri()
    result['start'] = o.Start()
    result['stop'] = o.Stop()

    fields_count = o.FieldsLength()
    fields = []
    for i in range(0, fields_count):
        fields.append(o.Fields(i))
    result['fields'] = fields
    shape_count = o.ShapeLength()
    shape = []
    for i in range(0, shape_count):
        gcp = SEAScope.types.gcp.deserialize(o.Shape(i))
        shape.append(gcp)
    result['shape'] = shape

    gcps_count = o.GcpsLength()
    gcps = []
    for i in range(0, gcps_count):
        gcp = SEAScope.types.gcp.deserialize(o.Gcps(i))
        gcps.append(gcp)
    result['gcps'] = gcps

    fill_values_count = o.FillValuesLength()
    fill_values = []
    for i in range(0, fill_values_count):
        fill_values.append(o.FillValues(i))
    result['fill_values'] = fill_values

    values_count = o.BufferLength()
    fmt = '<' + 'f' * values_count
    vs = struct.Struct(fmt)
    b_offset = o._tab.Offset(12)
    buffer_offset = flatbuffers.number_types.UOffsetTFlags.py_type(b_offset)
    vector_offset = o._tab.Vector(buffer_offset)
    values = vs.unpack_from(flatbuffers.compat.memoryview_type(o._tab.Bytes),
                            vector_offset)
    result['buffer'] = values

    return result
