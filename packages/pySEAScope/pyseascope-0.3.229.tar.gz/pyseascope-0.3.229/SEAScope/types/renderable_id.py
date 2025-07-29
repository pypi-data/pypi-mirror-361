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
This module handles the serialization and deserialization of the identifiers
for renderable objects.
"""

import logging
import flatbuffers
import SEAScope.API.RenderableId

logger = logging.getLogger(__name__)


def serialize(builder, rid_obj):
    """
    Serialize a renderable ID using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    rid_obj : dict
        Dictionary which contains information about the renderable ID to
        serialize

        It must have 5 keys:

        - ``granuleLevel`` : a :obj:`bool` that tells SEAScope if the targeted
          object is a granule (True) or a collection (False)

        - ``sourceId`` : a :obj:`int` which is the unique identifier of the
          data source which provided the targeted object

        - ``collectionId`` : a :obj:`int` which is the unique identifier
          (within the data source) of the targeted collection

        - ``granuleId`` : a :obj:`int` which is the unique identifier (within
          the data source) of the targeted granule

          Ignored if ``granuleLevel`` is False

        - ``variableId`` :a :obj:`int` which is the unique identifier (within
          the collection) of the targeted variable

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

    cls = SEAScope.API.RenderableId
    rid = cls.CreateRenderableId(builder,
                                 int(rid_obj['granuleLevel']),
                                 int(rid_obj['sourceId']),
                                 int(rid_obj['collectionId']),
                                 int(rid_obj['granuleId']),
                                 int(rid_obj['variableId']))

    return builder, rid


def deserialize(o):
    """
    Rebuild an identifier for a renderable object from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contain the renderable ID object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized renderable ID object as a dictionary.
    """
    result = {}
    result['granuleLevel'] = 0 < o.GranuleLevel()
    result['sourceId'] = o.SourceId()
    result['collectionId'] = o.CollectionId()
    result['granuleId'] = o.GranuleId()
    result['variableId'] = o.VariableId()
    return result
