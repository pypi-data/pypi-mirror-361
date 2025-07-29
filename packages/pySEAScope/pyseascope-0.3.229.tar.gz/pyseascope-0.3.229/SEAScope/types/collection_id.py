# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2016-09-09
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
This module handle the serialization of collection identifiers.
"""

import logging
import flatbuffers
import SEAScope.API.CollectionId

logger = logging.getLogger(__name__)


def serialize(builder, colid_obj):
    """
    Serializes a collection identifier using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    colid_obj : dict
        Dictionary which contains information about the collection to serialize
        It must have two keys:

        - sourceId : an :obj:`int` that identifies the data source which owns
          the collection
        - collectionId : an :obj:`int` that identifies the collection within
          the data source it belongs to

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

    cls = SEAScope.API.CollectionId
    cid = cls.CreateCollectionId(builder,
                                 int(colid_obj['sourceId']),
                                 int(colid_obj['collectionId']))

    return builder, cid


def deserialize(buf):
    """Not implemented"""
    pass
