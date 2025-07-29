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
This module handles the serialization and deserialization of rendering
configuration objects
"""

import logging
import flatbuffers
import SEAScope.API.RenderingCfg
import SEAScope.types.color
import SEAScope.types.renderable_id
import SEAScope.API.FilterMode

logger = logging.getLogger(__name__)

rendering_methods = {
    'RASTER': SEAScope.API.RenderingMethod.RenderingMethod.RASTER,
    'ARROWS': SEAScope.API.RenderingMethod.RenderingMethod.ARROWS,
    'BARBS': SEAScope.API.RenderingMethod.RenderingMethod.BARBS,
    'TRAJECTORIES': SEAScope.API.RenderingMethod.RenderingMethod.TRAJECTORIES,
    'DOTSCLOUD': SEAScope.API.RenderingMethod.RenderingMethod.DOTSCLOUD,
    'STREAMLINES': SEAScope.API.RenderingMethod.RenderingMethod.STREAMLINES,
    'RAWRGB': SEAScope.API.RenderingMethod.RenderingMethod.RAWRGB}
"""dict: Methods for rendering data in SEAScope.

Note that DOTSCLOUD is not supported by the current version of SEAScope
"""

filter_modes = {
    'NEAREST': SEAScope.API.FilterMode.FilterMode.NEAREST,
    'BILINEAR': SEAScope.API.FilterMode.FilterMode.BILINEAR}
"""dict: Rendering filters available in SEAScope. These filters are applied for
mapping pixels with data."""


def serialize(builder, cfg_obj):
    """
    Serialize a rendering configuration using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    cfg_obj : dict
        Dictionary which contains information about the rendering configuration
        to serialize

        It must have 15 keys:

        - ``rendered`` : a :obj:`bool` telling SEAScope if the associated
          target should be rendered or not (only relevant for collections)

        - ``logscale`` : a :obj:`bool` telling SEAScope to use a logarithmic
          scale when applying the colormap (True) or the default linear scale
          (False)

        - ``min`` : a :obj:`float` that SEAScope must use as the minimal value
          when applying the colormap

        - ``max`` : a :obj:`float` that SEAScope must use as the maximal value
          when applying the colormap

        - ``opacity`` : a :obj:`float` giving the opacity of the target. Its
          value belongs to the [0.0, 1.0] range: 0.0 is fully transparent, 1.0
          is completely opaque

        - ``zindex`` : a :obj:`float` that SEAScope uses to decide in which
          order the data should be rendered. Granules with a low zindex are
          rendered before granules with a high zindex

        - ``colormap`` : a :obj:`str` which identifies the colormap applied to
          the representation of the variable.

          A colormap identifier is only valid if there is a file in the
          ``colormaps`` directory whose name is the identifier suffixed by the
          ``.rgb`` extension.

        - ``renderMethod`` : a :obj:`str` that tells SEAScope which rendering
          method must be used to display the variable. The value should be a
          key of the :const:`SEAScope.types.rendering_cfg.rendering_methods`
          dictionary

        - ``particlesCount`` : an :obj:`int` which sets the size of the pool of
          animated particles.

          This value controls the density of the particles when using the
          streamlines rendering method.

          Increasing the density adds a toll on the GPU and may significatively
          reduce fluidity.

        - ``particleTTL`` : an :obj:`int` (deprecated)

        - ``streamlineLength`` : an :obj:`int` which tells SEAScope how many
          segments each streamline should be made of

        - ``streamlineSpeed`` : a :obj:`float` (deprecated)

        - ``filterMode`` : a :obj:`str` that tells SEAScope which filter to use
          when mapping pixels with data values. The value must be a key of the
          :const:`SEAScope.types.rendering_cfg.filter_modes` dictionary

        - ``target`` : a :obj:`dict` that identifies the target of the
          rendering configuration. The value must satisfy the requirements of
          the :func:`SEAScope.types.renderable_id.serialize` method.

        - ``color`` : a :obj:`dict` describing the uniform color that SEAScope
          will apply when rendering the target. The value must satisfy the
          requirements of the :func:`SEAScope.types.color.serialize` method.

          If both ``color`` and ``colormap`` are defined, then the colormap
          will be used and the color will be ignored.

        - ``billboardsSize`` : a :obj:float used by SEAScope to define the size
          of symbols when rendering data as arrows or barbs.

        - ``billboardsDensity`` : a :obj:float value between 0.0 and 1.0 that
          SEAScope uses to compute how many symbols it must draw when using the
          arrows or barbs renderers. A value of 0.0 means that symbols will be
          separated by a blank space which has the same size as one symbol.
          A value of 1.0 means that there is no blank space between visible
          symbols.

        - ``lineThickness`` : a :obj:float that tells SEAScope how thick lines
          should be (in pixels) when drawing trajectories or polylines.

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

    cls = SEAScope.API.RenderingCfg

    _rendered = cfg_obj['rendered']
    _logscale = cfg_obj['logscale']
    _min = cfg_obj['min']
    _max = cfg_obj['max']
    _opacity = cfg_obj['opacity']
    _zindex = cfg_obj['zindex']
    _colormap = builder.CreateString(cfg_obj['colormap'])
    _render_method = rendering_methods.get(cfg_obj['renderMethod'], None)
    _particles_count = int(cfg_obj['particlesCount'])
    _particle_ttl = int(cfg_obj['particleTTL'])
    _streamline_length = int(cfg_obj['streamlineLength'])
    _streamline_speed = cfg_obj['streamlineSpeed']
    _filter_mode = filter_modes.get(cfg_obj['filterMode'], None)
    _billboards_size = cfg_obj['billboardsSize']
    _billboards_density = cfg_obj['billboardsDensity']
    _line_thickness = cfg_obj['lineThickness']

    cls.RenderingCfgStart(builder)
    cls.RenderingCfgAddRendered(builder, _rendered)
    cls.RenderingCfgAddLogscale(builder, _logscale)
    cls.RenderingCfgAddMin(builder, _min)
    cls.RenderingCfgAddMax(builder, _max)
    cls.RenderingCfgAddOpacity(builder, _opacity)
    cls.RenderingCfgAddZindex(builder, _zindex)
    cls.RenderingCfgAddColormap(builder, _colormap)
    cls.RenderingCfgAddRenderMethod(builder, _render_method)
    cls.RenderingCfgAddParticlesCount(builder, _particles_count)
    cls.RenderingCfgAddParticleTTL(builder, _particle_ttl)
    cls.RenderingCfgAddStreamlineLength(builder, _streamline_length)
    cls.RenderingCfgAddStreamlineSpeed(builder, _streamline_speed)
    cls.RenderingCfgAddFilterMode(builder, _filter_mode)
    cls.RenderingCfgAddBillboardsSize(builder, _billboards_size)
    cls.RenderingCfgAddBillboardsDensity(builder, _billboards_density)
    cls.RenderingCfgAddLineThickness(builder, _line_thickness)

    _, _target = SEAScope.types.renderable_id.serialize(builder,
                                                        cfg_obj['target'])
    cls.RenderingCfgAddTarget(builder, _target)
    _, _color = SEAScope.types.color.serialize(builder, cfg_obj['color'])
    cls.RenderingCfgAddColor(builder, _color)
    cfg = cls.RenderingCfgEnd(builder)
    return builder, cfg


def deserialize(o):
    """
    Rebuild a rendering configuration from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contain the rendering configuration object serialized
        with FlatBuffers

    Returns
    -------
    dict
        The deserialized rendering configuration object as a dictionary.
    """
    cfg = {}
    cfg['rendered'] = 0 < o.Rendered()
    cfg['logscale'] = 0 < o.Logscale()
    cfg['min'] = o.Min()
    cfg['max'] = o.Max()
    cfg['opacity'] = o.Opacity()
    cfg['zindex'] = o.Zindex()
    cfg['color'] = SEAScope.types.color.deserialize(o.Color())
    cfg['colormap'] = o.Colormap()
    rendering = o.RenderMethod()
    for k, v in rendering_methods.items():
        if v == rendering:
            cfg['renderMethod'] = k
            break
    filter_mode = o.FilterMode()
    for k, v in filter_modes.items():
        if v == filter_mode:
            cfg['filterMode'] = k
            break
    cfg['particlesCount'] = o.ParticlesCount()
    cfg['particleTTL'] = o.ParticleTTL()
    cfg['streamlineLength'] = o.StreamlineLength()
    cfg['streamlineSpeed'] = o.StreamlineSpeed()
    cfg['billboardsSize'] = o.BillboardsSize()
    cfg['billboardsDensity'] = o.BillboardsDensity()
    cfg['lineThickness'] = o.LineThickness()
    cfg['target'] = SEAScope.types.renderable_id.deserialize(o.Target())

    return cfg
