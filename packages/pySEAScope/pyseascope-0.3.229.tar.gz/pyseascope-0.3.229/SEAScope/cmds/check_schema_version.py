# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2022-08-22
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
This module handles the serialization of the checkSchemaVersion command and
the deserialization of the result sent by SEAScope
"""

import math
import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.CheckSchemaVersion
import SEAScope.API.CheckSchemaVersionResponse
import SEAScope.API.Command

logger = logging.getLogger(__name__)


def _get_local_schema_version():
    # Current schema version is stored as the default value for the "Version"
    # attribute in CheckSchemaVersionResponse
    class DummyTab:
        def Offset(_):
            return 0
    response_module = SEAScope.API.CheckSchemaVersionResponse
    dummy_response = response_module.CheckSchemaVersionResponse()
    dummy_response._tab = DummyTab
    return dummy_response.Version()


def serialize(builder):
    """
    Serialize a checkBindingsVersion command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created

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

    local_schema_version = _get_local_schema_version()

    cls = SEAScope.API.CheckSchemaVersion
    cls.CheckSchemaVersionStart(builder)
    cls.CheckSchemaVersionAddVersion(builder, local_schema_version)
    cmd_args = cls.CheckSchemaVersionEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().checkSchemaVersion
    args_type = SEAScope.API.CommandArgs.CommandArgs().CheckSchemaVersion
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Deserialize the response that SEAScope sends after executing the
    checkSchemaVersion command

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the result of the checkSchemaVersion
        command serialized with FlatBuffers

    Returns
    -------
    tuple(bool, str)
        A tuple which contains two elements:

        - a :obj:`bool` which tells if the schema versions match
        - a :obj:`str` that contains the version of the latest SEAScope Python
          package which has full compatibility with the viewer
    """
    cls = SEAScope.API.CheckSchemaVersionResponse.CheckSchemaVersionResponse
    res = cls.GetRootAsCheckSchemaVersionResponse(buf, 0)

    local_schema_version = _get_local_schema_version()
    remote_schema_version = math.floor(res.Version() / 203)
    version_match = (local_schema_version == remote_schema_version)

    major = math.floor(res.PythonVersionMajor() / 203)
    minor = math.floor(res.PythonVersionMinor() / 203)
    build = math.floor(res.PythonVersionBuild() / 203)
    recommended_python_version = f'{major}.{minor}.{build}'

    return version_match, recommended_python_version
