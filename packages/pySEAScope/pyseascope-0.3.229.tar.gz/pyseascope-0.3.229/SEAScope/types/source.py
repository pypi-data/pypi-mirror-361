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
This module handles the serialization and deserialization of source objects
"""

import logging
import flatbuffers
import SEAScope.API.Source
import SEAScope.types.tag

logger = logging.getLogger(__name__)


def serialize(builder, src_obj):
    """
    Serialize a source using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    src_obj : dict
        Dictionary which contains information about the source to serialize
        It must have ten keys:

        - ``title`` : a :obj:`str` that SEAScope uses to designate the source

        - ``description``: a :obj:`str` that SEAScope can display to provide
          information about the source

        - ``tags`` : a :obj:`dict` which contains tags that describe the
          collection. SEAScope considers a (key, value) pair as a tag.

        - ``id`` : an :obj:`int` that SEAScope can uses as a unique identifier
          for the source

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

    cls = SEAScope.API.Source

    _title = builder.CreateString(src_obj['title'])
    _description = builder.CreateString(src_obj['description'])

    tags = []
    tags_len = len(src_obj['tags'].keys())
    for k, v in src_obj['tags'].items():
        _, tag = SEAScope.types.tag.serialize(builder, k, v)
        tags.append(tag)
    cls.SourceStartTagsVector(builder, tags_len)
    for t in tags:
        builder.PrependUOffsetTRelative(t)
    _tags = builder.EndVector(tags_len)

    cls.SourceStart(builder)
    cls.SourceAddId(builder, int(src_obj['id']))
    cls.SourceAddTitle(builder, _title)
    cls.SourceAddDescription(builder, _description)
    cls.SourceAddTags(builder, _tags)
    source = cls.SourceEnd(builder)

    return builder, source


def deserialize(o):
    """"""
    src_obj = {}
    src_obj['id'] = o.Id()
    src_obj['title'] = o.Title()
    src_obj['description'] = o.Description()
    src_obj['tags'] = {}
    tags_count = o.TagsLength()
    for i in range(0, tags_count):
        name, value = SEAScope.types.tag.deserialize(o.Tags(i))
        src_obj['tags'][name] = value

    return src_obj
