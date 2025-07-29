# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-15
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
This module handles the serialization of the setRendering command
"""

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CommandArgs
import SEAScope.API.SetRendering
import SEAScope.API.Command

logger = logging.getLogger(__name__)


def serialize(builder, rcfg):
    """
    Serialize a setRendering command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    rcfg : dict
        The rendering configuration to set in SEAScope. The :obj:`dict` must
        satisfy the requirements of the
        :func:`SEAScope.types.rendering_cfg.serialize` method

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

    _, _rcfg = SEAScope.types.rendering_cfg.serialize(builder, rcfg)

    cls = SEAScope.API.SetRendering
    cls.SetRenderingStart(builder)
    cls.SetRenderingAddCfg(builder, _rcfg)
    cmd_args = cls.SetRenderingEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().setRendering
    args_type = SEAScope.API.CommandArgs.CommandArgs().SetRendering
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
