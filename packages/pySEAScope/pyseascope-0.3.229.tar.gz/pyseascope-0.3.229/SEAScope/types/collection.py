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
This module handles the serialization and deserialization of collection objects
"""

import logging
import flatbuffers
import SEAScope.API.Collection
import SEAScope.types.renderable_id
import SEAScope.types.tag
import SEAScope.types.variable

logger = logging.getLogger(__name__)


def serialize(builder, collection_obj):
    """
    Serialize a collection using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    collection_obj : dict
        Dictionary which contains information about the collection to serialize
        It must have ten keys:

        - ``mustBeCurrent`` : a :obj:`bool` which tells SEAScope how its
          temporal filter must be applied for this collection.

          When this setting is set to true, the viewer will ignore granules
          whose time range does not contain the current datetime.
          It is the recommended behavior for collections whose granules cover
          the whole globe.

          When it is set to false, the viewer displayed the granules of the
          collection as long as their time range intersects the current time
          window (cf. timespans in the list of settings for the application
          configuration file).
          Use this behavior for collections of granules with a smaller spatial
          footprint or a sparse temporal coverage.

        - ``xSeamless`` : a :obj:`bool` which tells SEAScope that the granules
          of the collection have a 360° longitudinal cover

        - ``ySeamless`` : a :obj:`bool` which tells SEAScope that the granules
          of the collection have a 180° latitudinal cover

        - ``NEWSAligned`` : a :obj:`bool` which tells SEAScope that the axes of
          the data matrix are aligned witth the South-North and West-East axes

        - ``label`` : a :obj:`str` that SEAScope uses to designate the
          collection

        - ``tags`` : a :obj:`dict` which contains tags that describe the
          collection. SEAScope considers a (key, value) pair as a tag.

        - ``variables`` : a :obj:`list` of :obj:`dict` containing information
          about the variables defined for the collection.
          Each :obj:`dict` objects must have all the keys required by
          :func:`SEAScope.types.variable.serialize`

        - ``defaultVariable`` : a :obj:`int` which is the index of the default
          item in the ``variables`` list

        - ``id`` : a :obj:`dict` whose content can be used by SEAScope as a
          unique identifier for  the collection.
          It must have all the keys required by
          :func:`SEAScope.types.renderable_id.serialize`

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

    cls = SEAScope.API.Collection

    _must_be_current = collection_obj['mustBeCurrent']
    _x_seamless = collection_obj['xSeamless']
    _y_seamless = collection_obj['ySeamless']
    _news_aligned = collection_obj['NEWSAligned']
    _label = builder.CreateString(collection_obj['label'])

    tags = []
    tags_len = len(collection_obj['tags'].keys())
    for k, v in collection_obj['tags'].items():
        _, tag = SEAScope.types.tag.serialize(builder, k, v)
        tags.append(tag)
    cls.CollectionStartTagsVector(builder, tags_len)
    for t in tags:
        builder.PrependUOffsetTRelative(t)
    _tags = builder.EndVector(tags_len)

    variables = []
    vars_len = len(collection_obj['variables'])
    for var_obj in collection_obj['variables']:
        _, variable = SEAScope.types.variable.serialize(builder, var_obj)
        variables.append(variable)
    cls.CollectionStartVariablesVector(builder, vars_len)
    for v in variables:
        builder.PrependUOffsetTRelative(v)
    _variables = builder.EndVector(vars_len)

    _default_variable = int(collection_obj['defaultVariable'])
    _, _rid = SEAScope.types.renderable_id.serialize(builder,
                                                     collection_obj['id'])

    cls.CollectionStart(builder)
    cls.CollectionAddId(builder, _rid)
    cls.CollectionAddMustBeCurrent(builder, _must_be_current)
    cls.CollectionAddXSeamless(builder, _x_seamless)
    cls.CollectionAddYSeamless(builder, _y_seamless)
    cls.CollectionAddNewsAligned(builder, _news_aligned)
    cls.CollectionAddLabel(builder, _label)
    cls.CollectionAddTags(builder, _tags)
    cls.CollectionAddVariables(builder, _variables)
    cls.CollectionAddDefaultVariable(builder, _default_variable)
    collection = cls.CollectionEnd(builder)

    return builder, collection


def deserialize(buf):
    """
    Rebuild a collection from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the collection object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized collection object as a dictionary. Note that the
        "defaultVariable" key is lost in the process.
    """
    col_obj = {}
    col_obj['id'] = SEAScope.types.renderable_id.deserialize(buf.Id())
    col_obj['label'] = buf.Label()
    col_obj['mustBeCurrent'] = 0 < buf.MustBeCurrent()
    col_obj['xSeamless'] = 0 < buf.XSeamless()
    col_obj['ySeamless'] = 0 < buf.YSeamless()
    col_obj['NEWSAligned'] = 0 < buf.NewsAligned()
    col_obj['tags'] = {}
    tags_count = buf.TagsLength()
    for i in range(0, tags_count):
        name, value = SEAScope.types.tag.deserialize(buf.Tags(i))
        col_obj['tags'][name] = value

    col_obj['variables'] = []
    vars_count = buf.VariablesLength()
    for i in range(0, vars_count):
        v = SEAScope.types.variable.deserialize(buf.Variables(i))
        col_obj['variables'].append(v)

    return col_obj
