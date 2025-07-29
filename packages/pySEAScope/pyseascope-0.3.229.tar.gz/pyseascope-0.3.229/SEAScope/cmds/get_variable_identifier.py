# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2019-03-27
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
This module handles the serialization of the getVariableIdentifier command and
the deserialization of the result sent by SEAScope
"""

import logging
import flatbuffers
import SEAScope.API.GetVariableIdentifier
import SEAScope.API.GetVariableIdentifierResponse
import SEAScope.types.renderable_id

logger = logging.getLogger(__name__)


def serialize(builder, collection_label, variable_label):
    """
    Serialize a getVariableIdentifier command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    collection_label : str
        Label of the collection that contains the target variable
    variable_label : str
        Label of the target variable

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

    _c_label = builder.CreateString(collection_label)
    _v_label = builder.CreateString(variable_label)

    cls = SEAScope.API.GetVariableIdentifier
    cls.GetVariableIdentifierStart(builder)
    cls.GetVariableIdentifierAddCollectionLabel(builder, _c_label)
    cls.GetVariableIdentifierAddVariableLabel(builder, _v_label)
    cmd_args = cls.GetVariableIdentifierEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().getVariableIdentifier
    args_type = SEAScope.API.CommandArgs.CommandArgs().GetVariableIdentifier
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Deserialize the response that SEAScope sends after executing the
    getVariableIdentifier command

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the result of the getVariableIdentifier
        command serialized with FlatBuffers

    Returns
    -------
    dict
        The identifier found by SEAScope, which is the result produced by the
        :func:`SEAScope.types.renderable_id.deserialize` method (see source
        code for more details)
    """
    deserializer = SEAScope.types.renderable_id.deserialize
    _api_cls = SEAScope.API.GetVariableIdentifierResponse
    cls = _api_cls.GetVariableIdentifierResponse
    res = cls.GetRootAsGetVariableIdentifierResponse(buf, 0)
    _rid = res.Id()
    rid = deserializer(_rid)
    return rid
