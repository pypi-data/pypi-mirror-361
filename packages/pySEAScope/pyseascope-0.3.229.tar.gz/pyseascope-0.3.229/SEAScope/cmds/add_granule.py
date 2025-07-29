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
This module handles the serialization of the addGranule command
"""

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CommandArgs
import SEAScope.API.AddGranule
import SEAScope.API.Command
import SEAScope.types.granule_metadata
import SEAScope.types.granule_data
import SEAScope.types.renderable_id

logger = logging.getLogger(__name__)


def serialize(builder, cmd_obj):
    """
    Serialize a addGranule command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    cmd_obj : dict
        The granule information provided as a dict with three keys:

        - ``data`` : a :obj:`dict` which describes and contains the granule
          data.

          The dict must satisfy the requirements of the
          :func:`SEAScope.types.granule_data.serialize` method

        - ``metadata`` : a :obj:`dict` which contains the metadata of the
          granule.

          The dict must satisfy the requirements of the
          :func:`SEAScope.types.granule_data.serialize` method

        - ``id`` : a :obj:`dict` which contains the information for identifying
          the granule in SEAScope.

          The dict must satisfy the requirements of the
          :func:`SEAScope.types.renderable_id.serialize` method

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

    serializer = SEAScope.types.granule_data.serialize
    _, data = serializer(builder, cmd_obj['data'])
    serializer = SEAScope.types.granule_metadata.serialize
    _, metadata = serializer(builder, cmd_obj['metadata'])
    serializer = SEAScope.types.renderable_id.serialize
    _, rid = serializer(builder, cmd_obj['id'])

    cls = SEAScope.API.AddGranule
    cls.AddGranuleStart(builder)
    cls.AddGranuleAddId(builder, rid)
    cls.AddGranuleAddMetadata(builder, metadata)
    cls.AddGranuleAddData(builder, data)
    cmd_args = cls.AddGranuleEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().addGranule
    args_type = SEAScope.API.CommandArgs.CommandArgs().AddGranule
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Not implemented
    """
    pass
