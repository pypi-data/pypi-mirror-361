# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-10-11
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
This module handles the serialization and deserialization of IDF descriptor
objects
"""

import logging
import flatbuffers
import SEAScope.API.IDFDescriptor
import SEAScope.types.shape

logger = logging.getLogger(__name__)


def serialize(builder, obj):
    """
    Serialize an IDF descriptor using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    obj : dict
        Dictionary which contains information about the IDF descriptor to
        serialize

        It must have 6 keys:

        - ``uri`` : a :obj:`str` which is the address where SEAScope will find
          the granule

        - ``resolution`` : a :obj:`float` which is the resolution, in meters
          per cell of data, of the granule

        - ``subsampling_factor`` : an :obj:`int` which tells SEAScope how many
          times the data contained in the granule have been subsampled (by 2)
          compared to the full resolution data

        - ``xArity`` : an :obj:`int` which tells SEAScope how many columns it
          must allocate when reconstructing the data matrix

        - ``yArity`` : an :obj:`int` which tells SEAScope how many rows it must
          allocate when reconstructing the data matrix

        - ``shape`` : a :obj:`dict` that describes the shape of the granule.
          The value must satisfy the requirements of the
          :func:`SEAScope.types.shape.serialize` method

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

    uri = builder.CreateString(obj['uri'])
    resolution = obj['resolution']
    subsampling_factor = int(obj['subsampling_factor'])
    x_arity = int(obj['xArity'])
    y_arity = int(obj['yArity'])
    _, shape = SEAScope.types.shape.serialize(builder, obj['shape'])

    cls = SEAScope.API.IDFDescriptor
    cls.IDFDescriptorStart(builder)
    cls.IDFDescriptorAddUri(builder, uri)
    cls.IDFDescriptorAddResolution(builder, resolution)
    cls.IDFDescriptorAddXArity(builder, x_arity)
    cls.IDFDescriptorAddYArity(builder, y_arity)
    cls.IDFDescriptorAddShape(builder, shape)
    cls.IDFDescriptorAddSubsamplingFactor(builder, subsampling_factor)
    idf_descriptor = cls.IDFDescriptorEnd(builder)

    return builder, idf_descriptor


def deserialize(o):
    """
    Rebuild an IDF descriptor from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contain the IDF descriptor object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized IDF descriptor object as a dictionary.
    """
    result = {}
    result['uri'] = o.Uri()
    result['resolution'] = o.Resolution()
    result['xArity'] = o.XArity()
    result['yArity'] = o.YArity()
    result['shape'] = SEAScope.types.shape.deserialize(o.Shape())
    result['subsampling_factor'] = o.SubsamplingFactor()
    return result
