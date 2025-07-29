# vim: ts=4:sts=4:sw=4
#
# @author: <sylvain.herledan@oceandatalab.com>
# @date: 2017-05-02
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
This module contains the implementation of the processing server that can be
started from the command line with ``seascope-processor``
"""

import os
import sys
import numpy
import struct
import socket
import logging
import datetime
import tempfile
import threading

import SEAScope.lib
import SEAScope.lib.utils
import SEAScope.lib.plots

# Initialize Matplotlib backend
import matplotlib
matplotlib.use('Agg')


logger = logging.getLogger(__name__)


def serialize_extraction():
    """Handler called to fetch extracted data from SEAScope and save them in a
    file using the Numpy serialization format.

    Returns
    -------
    tuple(bool, str)
        A tuple which contains:

        - a :obj:`bool` set to True if the operation succeded
        - a :obj:`str` message containing the path of the output file
    """
    logger.info('Serializing extracted data...')
    now = datetime.datetime.utcnow()
    output_dir = tempfile.mkdtemp(suffix=now.strftime('%Y%m%dT%H%M%S'))
    output_path = os.path.join(output_dir, 'seascope_extract.pyo')

    granules = SEAScope.lib.get_extracted_data()
    SEAScope.lib.save_pyo(granules, output_path)

    logger.info('Done.')
    return True, '=> Serialization output saved in {}'.format(output_path)


def plot_extraction():
    """Handler called to fetch extracted data from SEAScope, render them as
    2D plots and save the result as PNG images.

    Returns
    -------
    tuple(bool, str)
        A tuple which contains:

        - a :obj:`bool` set to True if the operation succeded
        - a :obj:`str` message containing the path of the output directory
          where the PNG files have been saved
    """
    logger.info('Saving extracted data as PNGs...')
    now = datetime.datetime.utcnow()
    output_dir = tempfile.mkdtemp(suffix=now.strftime('%Y%m%dT%H%M%S'))

    granules = SEAScope.lib.get_extracted_data()

    for granule_uri in granules:
        granule_data = granules[granule_uri]['data']
        for field in granule_data:
            _data = numpy.flipud(granule_data[field])
            _uri = os.path.basename(granule_uri)

            output_file = '{}_{}.png'.format(_uri, field)
            output_path = os.path.join(output_dir, output_file)

            SEAScope.lib.plots.plot_2d_data(_uri, field, _data, output_path)

    return True, '=> PNGs generated for all granules in {}'.format(output_dir)


def plot_transect():
    """Handler called to fetch extracted data from SEAScope, render them as
    transects in a single plot and save the result as a PNG image.

    Returns
    -------
    tuple(bool, str)
        A tuple which contains:

        - a :obj:`bool` set to True if the operation succeded
        - a :obj:`str` message containing the path of the output PNG file
    """
    logger.info('Saving extracted data as PNGs...')
    now = datetime.datetime.utcnow()
    output_dir = tempfile.mkdtemp(suffix=now.strftime('%Y%m%dT%H%M%S'))

    granules = SEAScope.lib.get_extracted_data()

    if 'mask' not in granules:
        raise Exception('Missing mask in transects')

    dists = SEAScope.lib.get_dists(granules['mask'])

    transects = {}
    for granule_uri in granules:
        if 'mask' == granule_uri:
            continue

        granule = granules[granule_uri]
        for field in granule['data']:
            _uri = os.path.basename(granule_uri)
            uri = '{}: {}'.format(_uri, field)
            transects[uri] = granule['data'][field][0, :]

    output_file = '{}.png'.format('transects')
    output_path = os.path.join(output_dir, output_file)

    SEAScope.lib.plots.plot_transect(dists, transects, output_path)

    return True, '=> Result saved in {}'.format(output_path)


class ProcessingUnit(threading.Thread):
    """Thread that handles a single request sent by SEAScope.

    Parameters
    ----------
    s : socket:socket
        The socket connected to SEAScope
    """

    def __init__(self, s):
        super(ProcessingUnit, self).__init__()
        self.socket = s

    def run(self):
        """
        Method called when the thread execution starts.

        It parses the request sent by SEAScope, extracts an opcode and
        calls a processing handler accordingly.
        """
        buf = self.socket.recv(8)
        _opcode = struct.unpack('<Q', buf)
        opcode = _opcode[0]
        logger.debug('Received opcode {}'.format(opcode))
        if 0 == opcode:
            # noop
            pass
        elif 1 == opcode:
            ok, msg = plot_extraction()
            if not ok:
                logger.error(msg)
                return
            logger.info(msg)
        elif 2 == opcode:
            ok, msg = plot_transect()
            if not ok:
                logger.error(msg)
                return
            logger.info(msg)
        elif 3 == opcode:
            ok, msg = serialize_extraction()
            if not ok:
                logger.error(msg)
                return
            logger.info(msg)
        else:
            logger.error('Received unknown opcode {}'.format(opcode))

    def close(self):
        """Method called on thread termination.

        It makes sure that the socket is properly closed before the object is
        garbage-collected.
        """
        self.socket.close()


def bind_socket(s, interface='127.0.0.1'):
    """Bind a socket to an interface.

    The method tries to bind the default port (53450) first but it will
    fallback to the first port available if 53450 is already in use.

    Parameters
    ----------
    s : socket.socket
        The socket to bind
    interface : string
        The IP address to which the socket must be bound to


    Returns
    -------
    tuple(str, int)
        A tuple which contains two elements:

        - a :obj:`str` for the address to which the socket is actually bound to
        - a :obj:`int` for the port that the socket has managed to acquire
    """
    # Check default port first
    use_default = True
    port = 53450
    try:
        s.bind((interface, port))
        logger.info('Using default port {}'.format(port))
    except socket.error:
        # Try to get a free port
        logger.info('Default port {} already in use'.format(port))
        logger.info('Requesting another one...')
        use_default = False
        port = 0
        s.bind((interface, port))

    addr, port = s.getsockname()
    if use_default is False:
        logger.warn('\n{}'.format(''.join(['-'] * 80)))
        logger.warn('* seascope-processor is not listening on the default '
                    'port (already in use).\n*\n* You will have to '
                    'update SEAScope configuration manually for it to send \n'
                    '* processing requests to the right port: {}'.format(port))
        logger.warn('{}\n'.format(''.join(['-'] * 80)))
    return (addr, port)


def serve_forever():
    """Starts a sockets server that handles requests sent by SEAScope and
    creates a :class:`SEAScope.cli.server.ProcessingUnit` for each request to
    process.

    Returns
    -------
    tuple(bool, str)
        A tuple which contains two elements:

        - A :obj:`bool` set to False if an error occurs, True if everything
          went fine
        - A obj:`str` that contains the error message, or None if not relevant
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr, port = bind_socket(s)
        s.listen(15)
    except socket.error:
        _, e, _ = sys.exc_info()
        logger.error('{}'.format(e))
        return False, 'Failed to create socket'

    # TODO: find a way to tell SEAScope about the port
    logger.info('Listening on {}:{}'.format(addr, port))
    logger.info('Processing server is running.')
    while True:
        try:
            client_socket, address = s.accept()
            processing_unit = ProcessingUnit(client_socket)
            processing_unit.start()
        except KeyboardInterrupt:
            return True, None

    return False, 'Something went wrong'


def seascope_processor():
    """Method called when the user executes ``seascope-processor`` on the
    command line.

    It setups logging before starting the sockets server.
    """
    # Setup logging
    main_logger = logging.getLogger()
    main_logger.handlers = []
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    main_logger.addHandler(handler)
    main_logger.setLevel(logging.INFO)

    ok, msg = serve_forever()
    if not ok:
        logger.error(msg)
        sys.exit(1)
