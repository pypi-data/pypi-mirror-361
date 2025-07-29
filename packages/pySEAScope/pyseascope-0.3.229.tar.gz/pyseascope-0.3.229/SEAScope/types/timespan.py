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
This module handles the serialization and deserialization of timespan objects
"""

import logging
import flatbuffers
import SEAScope.API.Timespan

logger = logging.getLogger(__name__)


def serialize(builder, span_obj):
    """
    Serialize a timespan using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    span_obj : dict
        Dictionary which contains information about the timespan to serialize
        It must have three keys:

        - ``label`` : a :obj:`str` displayed by SEAScope to designate this
          timespan

        - ``pastOffset`` : an :obj:`int` that tells SEAScope when the timespan
          starts, as a positive number of seconds relative to SEAScope current
          datetime, i.e. ``start = current - pastOffset``

        - ``futureOffset`` : an :obj:`int` that tells SEAScope when the
          timespan ends, as a positive number of seconds relative to SEAScope
          current datetime, i.e. ``end = current + futureOffset``

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

    _label = builder.CreateString(span_obj['label'])
    _past = span_obj['pastOffset']
    _future = span_obj['futureOffset']
    cls = SEAScope.API.Timespan
    cls.TimespanStart(builder)
    cls.TimespanAddLabel(builder, _label)
    cls.TimespanAddPastOffset(builder, _past)
    cls.TimespanAddFutureOffset(builder, _future)
    timespan = cls.TimespanEnd(builder)

    return builder, timespan


def deserialize(o):
    """
    Rebuild a timespan from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the timespan object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized timespan object as a dictionary.
    """
    result = {}
    result['label'] = o.Label()
    result['pastOffset'] = o.PastOffset()
    result['futureOffset'] = o.FutureOffset()
    return result
