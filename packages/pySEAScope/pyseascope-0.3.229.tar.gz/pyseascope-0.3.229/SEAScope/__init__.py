# vim: ts=4:sts=4:sw=4
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

import sys

if (3 == sys.version_info.major) and (11 < sys.version_info.minor):
    if 'imp' not in sys.modules.keys():
        # Monkey-patch so that flatbuffers v1.x can be used
        import SEAScope.flatbuffers1_compat
        sys.modules['imp'] = SEAScope.flatbuffers1_compat

__description__ = ('Python bindings to interact with the SEAScope application')
__version__ = '0.3'
__author__ = ('Sylvain Herlédan <sylvain.herledan@oceandatalab.com',)
__author_email__ = 'seascope@oceandatalab.com'
__url__ = 'https://seascope.oceandatalab.com/python.html'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Science/Research',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows :: Windows 10',
                   'Operating System :: Microsoft :: Windows :: Windows 8.1',
                   'Operating System :: Microsoft :: Windows :: Windows 8',
                   'Operating System :: Microsoft :: Windows :: Windows 7',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Scientific/Engineering :: GIS']
