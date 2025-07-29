# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-08
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
This module handles the serialization and deserialization of timestep objects
"""

import logging
import flatbuffers
import SEAScope.API.Timestep

logger = logging.getLogger(__name__)


def serialize(builder, step_obj):
    """
    Serialize a timestep using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    step_obj : dict
        Dictionary which contains information about the timestep to serialize
        It must have two keys:

        - ``label`` : a :obj:`str` displayed by SEAScope to designate this
          timestep

        - ``step`` : an :obj:`int` that gives the size of the step in seconds

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

    _label = builder.CreateString(step_obj['label'])
    _step = step_obj['step']
    cls = SEAScope.API.Timestep
    cls.TimestepStart(builder)
    cls.TimestepAddLabel(builder, _label)
    cls.TimestepAddStep(builder, _step)
    timestep = cls.TimestepEnd(builder)

    return builder, timestep


def deserialize(o):
    """
    Rebuild a timestep from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the timestep object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized timestep object as a dictionary.
    """
    result = {}
    result['label'] = o.Label()
    result['step'] = o.Step()
    return result
