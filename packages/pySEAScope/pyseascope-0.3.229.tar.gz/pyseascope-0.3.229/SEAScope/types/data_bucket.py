# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-11-02
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
This module handles the serialization of data bucket objects
"""

import logging
import flatbuffers
import SEAScope.API.DataBucket
import SEAScope.types.data_info

logger = logging.getLogger(__name__)


def serialize(builder, bucket_obj):
    """
    Serialize a data bucket using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    bucket_obj : :obj:`dict`
        Dictionary which contains information about the data bucket to
        serialize.
        It must have 2 keys:

        - ``info`` : a :obj:`dict` providing information about the data
          contained in the bucket. It must have all the keys required by
          :func:`SEAScope.types.data_info.serialize`

        - ``data`` : a :obj:`list` of `numpy.uint8` which contains values
          packed as unsigned bytes

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

    _, info = SEAScope.types.data_info.serialize(builder, bucket_obj['info'])

    cls = SEAScope.API.DataBucket

    buffer_len = len(bucket_obj['buffer'])
    cls.DataBucketStartBufferVector(builder, buffer_len)
    if '<' == bucket_obj['buffer'].dtype.str[0]:
        little_endian_data = bucket_obj['buffer']
    else:
        little_endian_data = bucket_obj['buffer'].byteswap(inplace=False)

    uoffset_t = flatbuffers.number_types.UOffsetTFlags

    # Compute how much memory is required (including alignment)
    _data_size = little_endian_data.itemsize * little_endian_data.size
    data_size = uoffset_t.py_type(_data_size)

    # Shift head
    builder.head = uoffset_t.py_type(builder.Head() - data_size)

    # Write data
    bytes_data = little_endian_data.tobytes(order='C')
    builder.Bytes[builder.Head():builder.Head() + data_size] = bytes_data
    data_buffer = builder.EndVector(buffer_len)

    cls.DataBucketStart(builder)
    cls.DataBucketAddInfo(builder, info)
    cls.DataBucketAddBuffer(builder, data_buffer)
    bucket = cls.DataBucketEnd(builder)

    return builder, bucket


def deserialize(o):
    """Not implemented"""
    pass
