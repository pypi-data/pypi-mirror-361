# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-11-03
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
This module handles the serialization of granule data objects
"""

import logging
import flatbuffers
import SEAScope.API.GranuleData
import SEAScope.types.data_bucket

logger = logging.getLogger(__name__)


def serialize(builder, data_obj):
    """
    Serialize a granule data using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    data_obj : dict
        Dictionary which contains information about the granule data to
        serialize. Its keys must be the name of the data fields and its values
        must be :obj:`dict` objects that satisfy the requirements of the
        :func:`SEAScope.types.data_bucket.serialize` method


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

    cls = SEAScope.API.GranuleData

    # Identify fields stored as unsigned bytes
    uint8_fields = [_ for _ in data_obj.keys()
                    if 'uint8' == data_obj[_]['info']['dataType']]

    _fields = []
    for field in uint8_fields:
        _field = builder.CreateString(field)
        _fields.append(_field)
    fields_len = len(_fields)
    cls.GranuleDataStartFieldsVector(builder, fields_len)
    for _field in _fields:
        builder.PrependUOffsetTRelative(_field)
    fields_vector = builder.EndVector(fields_len)

    _data = []
    for field in uint8_fields:
        _, _d = SEAScope.types.data_bucket.serialize(builder, data_obj[field])
        _data.append(_d)
    cls.GranuleDataStartBucketsVector(builder, fields_len)
    for _d in _data:
        builder.PrependUOffsetTRelative(_d)
    buckets = builder.EndVector(fields_len)

    # Identify fields stored as floats
    float_fields = [_ for _ in data_obj.keys()
                    if 'float32' == data_obj[_]['info']['dataType']]

    _fields = []
    for field in float_fields:
        _field = builder.CreateString(field)
        _fields.append(_field)
    fields_len = len(_fields)
    cls.GranuleDataStartFloatFieldsVector(builder, fields_len)
    for _field in _fields:
        builder.PrependUOffsetTRelative(_field)
    float_fields_vector = builder.EndVector(fields_len)

    _data = []
    for field in float_fields:
        _, _d = SEAScope.types.data_bucket.serialize(builder, data_obj[field])
        _data.append(_d)
    cls.GranuleDataStartBucketsVector(builder, fields_len)
    for _d in _data:
        builder.PrependUOffsetTRelative(_d)
    float_buckets = builder.EndVector(fields_len)

    cls.GranuleDataStart(builder)
    cls.GranuleDataAddFields(builder, fields_vector)
    cls.GranuleDataAddBuckets(builder, buckets)
    cls.GranuleDataAddFloatFields(builder, float_fields_vector)
    cls.GranuleDataAddFloatBuckets(builder, float_buckets)
    g_data = cls.GranuleDataEnd(builder)

    return builder, g_data


def deserialize(o):
    """
    Not implemented
    """
    pass
