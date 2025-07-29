# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-07
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
This module handles the serialization and deserialization of tag objects
"""

import logging
import flatbuffers
import SEAScope.API.Tag

logger = logging.getLogger(__name__)


def serialize(builder, name, value):
    """
    Serialize a timestep using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    name : str
        Name of the tag
    value : str
        Value of the tag. If the tag value is not a string, make sure to
        convert it to :obj:`str` before passing it to this method

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
    _name = builder.CreateString(name)
    _value = builder.CreateString(value)
    SEAScope.API.Tag.TagStart(builder)
    SEAScope.API.Tag.TagAddName(builder, _name)
    SEAScope.API.Tag.TagAddValue(builder, _value)
    tag = SEAScope.API.Tag.TagEnd(builder)
    return builder, tag


def deserialize(t):
    """
    Rebuild a tag from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the tag object serialized with FlatBuffers

    Returns
    -------
    tuple(:obj:`str`, :obj:`str`)
        The deserialized tag as a (name, value) pair.
    """
    return t.Name(), t.Value()
