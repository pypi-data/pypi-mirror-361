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
This module handles the serialization of the setNearestMode command
"""

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CommandArgs
import SEAScope.API.SetNearestMode
import SEAScope.API.Command

logger = logging.getLogger(__name__)


def serialize(builder, active):
    """
    Serialize a setTimestep command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    active : bool
        If this value is True, then SEAScope will activate the "nearest" mode
        of the timeline

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

    cls = SEAScope.API.SetNearestMode
    cls.SetNearestModeStart(builder)
    cls.SetNearestModeAddActive(builder, active)
    cmd_args = cls.SetNearestModeEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().setNearestMode
    args_type = SEAScope.API.CommandArgs.CommandArgs().SetNearestMode
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize():
    """
    Not implemented
    """
    pass
