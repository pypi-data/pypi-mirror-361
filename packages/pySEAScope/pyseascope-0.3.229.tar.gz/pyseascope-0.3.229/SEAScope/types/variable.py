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
This module handles the serialization and deserialization of variable objects
"""

import logging
import flatbuffers
import SEAScope.API.Variable
import SEAScope.API.RenderingMethod
import SEAScope.types.tag
import SEAScope.types.rendering_cfg

logger = logging.getLogger(__name__)
rendering_methods = SEAScope.types.rendering_cfg.rendering_methods


def serialize(builder, var_obj):
    """
    Serialize a variable using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    var_obj : dict
        Dictionary which contains information about the variable to serialize
        It must have five keys:

        - ``label`` : a :obj:`str` that SEAScope uses to designate the variable

        - ``units`` : a :obj:`str` for the units of the variable

        - ``fields`` : a :obj:`list` of :obj:`str` which contains the name of
          the data fields that must be read in order to recompose the variable.
          For example the U and V components for a vectorfield, or three
          channels for RGB images

        - ``tags`` : a :obj:`dict` which contains tags that describe the
          variable. SEAScope considers a (key, value) pair as a tag.

        - ``defaultRenderingMethod`` : a :obj:`str` that designates the
          rendering method that must be used by default for this variable.
          This parameter must be one of the keys of the
          :const:`SEAScope.types.rendering_cfg.rendering_methods` dictionary


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

    _id = int(var_obj['id'])
    _label = builder.CreateString(var_obj['label'])
    _units = builder.CreateString(var_obj['units'])
    fields_buffer = []
    for field in var_obj['fields']:
        _field = builder.CreateString(field)
        fields_buffer.append(_field)
    fields_len = len(fields_buffer)
    SEAScope.API.Variable.VariableStartFieldsVector(builder, fields_len)
    for t in fields_buffer:
        builder.PrependUOffsetTRelative(t)
    _fields = builder.EndVector(fields_len)

    tags_buffer = []
    for k, v in var_obj['tags'].items():
        _, _tag = SEAScope.types.tag.serialize(builder, k, v)
        tags_buffer.append(_tag)
    tags_len = len(tags_buffer)
    SEAScope.API.Variable.VariableStartTagsVector(builder, tags_len)
    for t in tags_buffer:
        builder.PrependUOffsetTRelative(t)
    _tags = builder.EndVector(tags_len)

    rendering = var_obj['defaultRenderingMethod']
    _default_rendering = rendering_methods.get(rendering, None)

    SEAScope.API.Variable.VariableStart(builder)
    SEAScope.API.Variable.VariableAddId(builder, _id)
    SEAScope.API.Variable.VariableAddLabel(builder, _label)
    SEAScope.API.Variable.VariableAddUnits(builder, _units)
    SEAScope.API.Variable.VariableAddFields(builder, _fields)
    SEAScope.API.Variable.VariableAddTags(builder, _tags)
    SEAScope.API.Variable.VariableAddDefaultRenderingMethod(builder,
                                                            _default_rendering)
    variable = SEAScope.API.Variable.VariableEnd(builder)
    return builder, variable


def deserialize(v):
    """
    Rebuild a variable from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the variable object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized variable object as a dictionary.
    """
    v_obj = {}
    v_obj['id'] = v.Id()
    v_obj['label'] = v.Label()
    v_obj['units'] = v.Units()
    fields_count = v.FieldsLength()
    v_obj['fields'] = [v.Fields(x) for x in range(0, fields_count)]
    tags_count = v.TagsLength()
    v_obj['tags'] = {}
    for i in range(0, tags_count):
        name, value = SEAScope.types.tag.deserialize(v.Tags(i))
        v_obj['tags'][name] = value

    v_obj['defaultRenderingMethod'] = 'NONE'
    rendering = v.DefaultRenderingMethod()
    for k, v in rendering_methods.items():
        if v == rendering:
            v_obj['defaultRenderingMethod'] = k
            break
    return v_obj
