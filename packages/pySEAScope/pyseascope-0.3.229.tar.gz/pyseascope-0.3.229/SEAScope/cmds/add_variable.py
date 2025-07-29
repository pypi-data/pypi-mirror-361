# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-06
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
This module handles the serialization of the addVariable command
"""

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CommandArgs
import SEAScope.API.AddVariable
import SEAScope.API.Command
import SEAScope.API.BasicResponse

import SEAScope.types.renderable_id
import SEAScope.types.variable

logger = logging.getLogger(__name__)


def serialize(builder, target, var_obj):
    """
    Serialize a addVariable command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    target : dict
        The identifier that must be used for the new variable. The dict must
        satisfy the requirements of the
        :func:`SEAScope.types.renderable_id.serialize` method
    var_obj : dict
        The parameters of the variable to add. The dict must satisfy the
        requirements of the
        :func:`SEAScope.types.variable.serialize` method

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

    _, _variable = SEAScope.types.variable.serialize(builder, var_obj)
    _, _rid = SEAScope.types.renderable_id.serialize(builder, target)

    cls = SEAScope.API.AddVariable
    cls.AddVariableStart(builder)
    cls.AddVariableAddCollectionId(builder, _rid)
    cls.AddVariableAddVariable(builder, _variable)
    cmd_args = cls.AddVariableEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().addVariable
    args_type = SEAScope.API.CommandArgs.CommandArgs().AddVariable
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Deserialize response sent by SEAScope after executing the addVariable
    command.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the result of the addVariable command
        serialized with FlatBuffers

    Returns
    -------
    dict
        The result of the addVariable command. The dict contains two keys:

        - ``ok`` : a :obj:`bool` representing the success (True) or failure
          (False) of the command execution

        - ``msg`` : a :obj:`str` providing details in case of failure
    """
    cls = SEAScope.API.BasicResponse.BasicResponse
    res = cls.GetRootAsBasicResponse(buf, 0)
    return {'ok': res.Success(), 'msg': res.Message().decode('utf-8')}
