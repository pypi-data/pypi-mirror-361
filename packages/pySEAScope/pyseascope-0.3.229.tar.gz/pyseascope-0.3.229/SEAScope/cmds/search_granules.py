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
This module handles the serialization of the searchGranules command and the
deserialization of the results sent by SEAScope
"""

import logging
import flatbuffers
import SEAScope.API.OpCode
import SEAScope.API.SearchGranules
import SEAScope.API.SearchGranulesResponse
import SEAScope.API.Command
import SEAScope.types.collection_id
import SEAScope.types.granule_metadata

logger = logging.getLogger(__name__)


def serialize(builder, search_obj):
    """
    Serialize a searchGranules command using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    search_obj : dict

        - collections : a :obj:`list` of :obj:`dict` which tells SEAScope the
          collections it must consider during the search. The dict values must
          satisfy the requirements of the
          :func:`SEAScope.types.collection_id.serialize` method

        - current : an :obj:`int` which acts in the same way as the current
          datetime of the timeline. Expressed in seconds since
          1970-01-01T00:00:00Z

          If a collection has the ``mustBeCurrent`` flag set to True, then
          SEAScope will only return the granules for this collection if
          ``current`` belongs to [granule.start, granule.stop[

        - start : an :obj:`int` which is the lower time bound used by SEAScope
          when searching for granules, expressed in seconds since
          1970-01-01T00:00:00Z.

          In interactive usage of SEAScope, this has the ``currentDatetime -
          pastOffset`` value

        - stop : an :obj:`int` which is the upper bound used by SEAScope when
          searching for granules, expressed in seconds since
          1970-01-01T00:00:00Z.

          In interactive usage of SEAScope, this has the ``currentDatetime +
          futureOffset`` value

        - zoom : a :obj:`float` that tells SEAScope at which altitude the
          camera should be during the search. It has an effect on the
          resolution of the granules returned in the results.

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

    cls = SEAScope.API.SearchGranules

    collectionsOffsets = 0
    cls.SearchGranulesStartCollectionsVector(builder,
                                             len(search_obj['collections']))
    for collection in search_obj['collections']:
        SEAScope.types.collection_id.serialize(builder, collection)
    collectionsOffsets = builder.EndVector(len(search_obj['collections']))

    cls.SearchGranulesStart(builder)
    cls.SearchGranulesAddCurrent(builder, search_obj['current'])
    cls.SearchGranulesAddStart(builder, search_obj['start'])
    cls.SearchGranulesAddStop(builder, search_obj['stop'])
    cls.SearchGranulesAddZoom(builder, search_obj['zoom'])
    cls.SearchGranulesAddCollections(builder, collectionsOffsets)
    cmd_args = cls.SearchGranulesEnd(builder)

    opcode = SEAScope.API.OpCode.OpCode().searchGranules
    args_type = SEAScope.API.CommandArgs.CommandArgs().SearchGranules
    SEAScope.API.Command.CommandStart(builder)
    SEAScope.API.Command.CommandAddOpcode(builder, opcode)
    SEAScope.API.Command.CommandAddArgsType(builder, args_type)
    SEAScope.API.Command.CommandAddArgs(builder, cmd_args)
    cmd = SEAScope.API.Command.CommandEnd(builder)

    return builder, cmd


def deserialize(buf):
    """
    Deserialize the response that SEAScope sends after executing the
    searchGranules command

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the result of the searchGranules command
        serialized with FlatBuffers

    Returns
    -------
    list of dict
        The metadata of the granules found by SEAScope. Each dict is the
        result of the :func:`SEAScope.types.granule_metadata.deserialize`
        method (see source code for more details)
    """
    deserializer = SEAScope.types.granule_metadata.deserialize
    cls = SEAScope.API.SearchGranulesResponse.SearchGranulesResponse
    res = cls.GetRootAsSearchGranulesResponse(buf, 0)

    granules_len = res.GranulesLength()
    return [deserializer(res.Granules(x)) for x in range(0, granules_len)]
