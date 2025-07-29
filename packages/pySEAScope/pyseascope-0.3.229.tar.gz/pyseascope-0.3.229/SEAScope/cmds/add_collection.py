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

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CommandArgs
import SEAScope.API.AddCollection
import SEAScope.API.Command

import SEAScope.types.collection

logger = logging.getLogger(__name__)


def serialize(builder, collection_obj):
    """
    Parameters
    ----------
    builder : flatbuffers.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    collection_obj : dict
        Dictionary which contains information about the collection to add.

        The dict must satisfy the requirements of the
        :func:`SEAScope.types.collection.serialize` method

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

    _, collection = SEAScope.types.collection.serialize(builder,
                                                        collection_obj)

    cls = SEAScope.API.AddCollection
    cls.AddCollectionStart(builder)
    cls.AddCollectionAddCollection(builder, collection)
    cmd_args = cls.AddCollectionEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().addCollection
    args_type = SEAScope.API.CommandArgs.CommandArgs().AddCollection
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Deserialize response sent by SEAScope after executing the addCollection
    command.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the result of the addCollection command
        serialized with FlatBuffers

    Returns
    -------
    dict
        The result of the addCollection command. The dict contains two keys:

        - ``ok`` : a :obj:`bool` representing the success (True) or failure
          (False) of the command execution

        - ``msg`` : a :obj:`str` providing details in case of failure
    """
    cls = SEAScope.API.BasicResponse.BasicResponse
    res = cls.GetRootAsBasicResponse(buf, 0)
    return {'ok': res.Success(), 'msg': res.Message().decode('utf-8')}
