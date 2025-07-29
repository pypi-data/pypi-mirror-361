# vim: set ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
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
This module provides methods for plotting the data extracted by SEAScope.
"""

import logging

logger = logging.getLogger(__name__)


def plot_2d_data(source_name, field_name, field_data, output_path):
    """Plot data extracted by SEAScope using a polygon.

    Parameters
    ----------
    source_name : str
        Name of the source (granule) data has been extracted from
    field_name : str
        Name of the extracted field
    field_data : numpy.array
        Extracted data (for a single field/channel)
    output_path : str
        Path of the file wherein the plot will be saved
    """
    import matplotlib
    import matplotlib.pyplot
    slice_size = 100
    slices = range(0, len(source_name), slice_size)
    wrapped_srcname = [source_name[i:i+slice_size] for i in slices]

    fig = matplotlib.pyplot.figure(1, figsize=(10, 10), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1], visible=True)
    ax.set_axis_off()
    matplotlib.pyplot.figtext(.5, 1.0, '\n'.join(wrapped_srcname), fontsize=10,
                              ha='center', figure=fig)
    matplotlib.pyplot.figtext(.5, 0.95, field_name, fontsize=16, ha='center',
                              figure=fig)
    _cmap = matplotlib.pyplot.get_cmap('jet')
    ax.imshow(field_data, cmap=_cmap, interpolation='nearest')

    fig.savefig(output_path, bbox_inches='tight')
    matplotlib.pyplot.close()


def plot_transect(dists, transects, output_path):
    """Plot data extracted by SEAScope using a polyline (transect).

    Parameters
    ----------
    dists : :obj:list of :obj:float
        Cumulative distance from origin to each point of the transect, in
        kilometers
    transects: :obj:dict
        Values extracted along the polyline for each (granule, field) pair
    output_path : str
        Path of the file wherein the plot will be saved
    """
    import matplotlib
    import matplotlib.pyplot
    cmap = matplotlib.pyplot.get_cmap('hsv', 1 + len(transects.keys()))

    fig = matplotlib.pyplot.figure(1, figsize=(10, 10), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1], visible=True)
    ax.set_xlabel('Distance (km)')

    k = 0
    for uri in transects:
        slice_size = 120
        slices = range(0, len(uri), slice_size)
        wrapped_uri = [uri[i:i+slice_size] for i in slices]

        ax.plot(dists, transects[uri], c=cmap(k), label='\n'.join(wrapped_uri))
        k = k + 1

    legend = matplotlib.pyplot.legend(bbox_to_anchor=(0., 1.02, 1., .102),
                                      loc=3, ncol=1, mode="expand",
                                      borderaxespad=0.)
    matplotlib.pyplot.setp(legend.get_title(), fontsize='xx-small')

    fig.savefig(output_path, bbox_inches='tight')
    matplotlib.pyplot.close()
