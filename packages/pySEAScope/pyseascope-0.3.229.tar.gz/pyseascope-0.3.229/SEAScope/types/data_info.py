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
This module handles the serialization of data info objects
"""

import logging
import flatbuffers
import SEAScope.API.DataInfo
import SEAScope.API.DataType

logger = logging.getLogger(__name__)
data_types = {
    'none': SEAScope.API.DataType.DataType.NONE,
    'uint8': SEAScope.API.DataType.DataType.UBYTE,
    'ushort16': SEAScope.API.DataType.DataType.USHORT,
    'uint32': SEAScope.API.DataType.DataType.UINT,
    'float32': SEAScope.API.DataType.DataType.FLOAT32}
"""
dict: Data types that can be used to store information in SEAScope. Beware:
SEAScope expects some values to have a specific type and will probably crash
or return an error if a value with another type is provided.
"""


def serialize(builder, info_obj):
    """
    Serialize a granule data info using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    info_obj : dict
        Dictionary which contains information about the data
        to serialize

        It must have  keys:

        - ``offsets`` : a :obj:`list` of :obj:`float` for the offset used when
          packing the data values (``packed = (values - offset) / scale``).

          One value per channel contained in the data matrix

        - ``scaleFactors`` : a :obj:`list` of `float` for the scale factors
          used when packing the data values (``packed = (values - offset) /
          scale``)

          One value per channel contained in the data matrix

        - ``fillValues`` : a :obj:`list` of :obj:`float` for the fill values
          that have been stored in the data matrix to replace missing/invalid
          data. Note that the fill values in this list belong to the packed
          values domain.

          One value per channel contained in the data matrix

        - ``dataType`` : a :obj:`str` which identifies the type to allocate for
          the values contained in the data matrix. Its value must be a key of
          the :const:`SEAScope.types.data_info.data_types`` dictionary.

          Only ``uint8`` is supported at the moment

        - ``channels`` : an :obj:`int` for the number of channels/fields
          contained in the data matrix

        - ``xArity`` : an :obj:`int` which tells SEAScope how many columns it
          must allocate when reconstructing the data matrix

        - ``yArity`` : an :obj:`int` which tells SEAScope how many rows it
          must allocate when reconstructing the data matrix

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

    cls = SEAScope.API.DataInfo

    offsets_len = len(info_obj['offsets'])
    cls.DataInfoStartOffsetsVector(builder, offsets_len)
    for v in info_obj['offsets'][::-1]:
        builder.PrependFloat32(v)
    offsets = builder.EndVector(offsets_len)

    scales_len = len(info_obj['scaleFactors'])
    cls.DataInfoStartScaleFactorsVector(builder, scales_len)
    for v in info_obj['scaleFactors'][::-1]:
        builder.PrependFloat32(v)
    scale_factors = builder.EndVector(scales_len)

    fills_len = len(info_obj['fillValues'])
    cls.DataInfoStartFillValuesVector(builder, fills_len)
    for v in info_obj['fillValues'][::-1]:
        builder.PrependFloat32(v)
    fill_values = builder.EndVector(fills_len)

    _data_type = data_types.get(info_obj['dataType'], data_types['none'])

    cls.DataInfoStart(builder)
    cls.DataInfoAddChannels(builder, int(info_obj['channels']))
    cls.DataInfoAddXArity(builder, int(info_obj['xArity']))
    cls.DataInfoAddYArity(builder, int(info_obj['yArity']))
    cls.DataInfoAddDataType(builder, _data_type)
    cls.DataInfoAddOffsets(builder, offsets)
    cls.DataInfoAddScaleFactors(builder, scale_factors)
    cls.DataInfoAddFillValues(builder, fill_values)
    data_info = cls.DataInfoEnd(builder)

    return builder, data_info


def deserialize(o):
    """
    Not implemented
    """
    pass
