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
This module handles the serialization and deserialization of granule metadata
objects
"""

import logging
import flatbuffers
import SEAScope.API.GranuleMetadata
import SEAScope.API.DataModel
import SEAScope.types.idf_descriptor

logger = logging.getLogger(__name__)
data_models = {'LAT_LON': SEAScope.API.DataModel.DataModel.LAT_LON,
               'Y_X': SEAScope.API.DataModel.DataModel.Y_X,
               'NJ_NI': SEAScope.API.DataModel.DataModel.NJ_NI,
               'ROW_CELL': SEAScope.API.DataModel.DataModel.ROW_CELL,
               'TIME_STATION': SEAScope.API.DataModel.DataModel.TIME_STATION,
               'TIME': SEAScope.API.DataModel.DataModel.TIME}
"""dict: Data models supported by SEAScope.
"""


def serialize(builder, obj):
    """
    Serialize a granule metadata using FlatBuffers.

    Parameters
    ----------
    builder : flatbuffers.builder.Builder
        The FlatBuffers builder instance which serializes data. If this
        parameter is None, then a new builder will be created
    obj : dict
        Dictionary which contains information about the shape to serialize
        It must have between 8 and 21 keys:

        - ``sourceId`` : an :obj:`int` which is the unique identifier for the
          source which provides the granule

        - ``collectionId`` : an :obj:`int` which is the unique identifier
          (within the data source) for the collection that owns the granule

        - ``granuleId`` : an :obj:`int` which is the unique identifier (within
          the data source) for the granule

        - ``dataId`` : a :obj:`str` which is the name of the granule. As for
          the ``granuleId`` it should remain unique within a data source

        - ``dataModel`` : a :obj:`str` that identifies the data model used to
          store the granule data. The value must be a key of the
          :const:`SEAScope.types.granule_metadata.data_models` dictionary

        - ``start`` : an :obj:`int` which is the first time when data is
          available in the granule, in milliseconds since
          1970-01-01T00:00:00.000Z

        - ``stop`` : an :obj:`int` which is the first time after ``start`` when
          data is not available anymore, in milliseconds since
          1970-01-01T00:00:00.000Z

        - ``uris`` : a :obj:`list` of :obj:`dict`. The elements of the list
          describe the files attached to the granule and must satisfy the
          requirements of the :func:`SEAScope.types.idf_descriptor.serialize`
          method

        - ``title`` : an optional :obj:`str` for the title/long name of the
          granule

        - ``institution`` : an optional :obj:`str` for the name of the
          institution which provided the granule

        - ``comment`` : an optional :obj:`str` for any comment about the
          granule

        - ``file_id`` : an optional :obj:`str` for an identifier or path of the
          original file which has been converted to IDF

        - ``product_version``: an optional :obj:`str` for the version of the
          product

        - ``lon_min`` : an optional :obj:`float` for the min longitude of the
          spatial coverage

        - ``lon_max`` : an optional :obj:`float` for the max longitude of the
          spatial coverage

        - ``lat_min`` : an optional :obj:`float` for the min latitude of the
          spatial coverage

        - ``lat_max`` : an optional :obj:`float` for the max latitude of the
          spatial coverage

        - ``creator_email``: an optional :obj:`str` the email address of the
          person who generated the IDF file

        - ``station_id`` : an optional :obj:`str` for the unique identifier of
          the station that provided the measurements contained in the granule

        - ``platform`` : an optional :obj:`str` for the name or identifier of
          the platform which hosts the sensors that provided the measurements

        - ``sensor`` : an optional :obj:`str` for the name or identifier of the
          sensor that measured the values contained in the granule

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

    cls = SEAScope.API.GranuleMetadata

    src_id = int(obj['sourceId'])
    col_id = int(obj['collectionId'])
    gra_id = int(obj['granuleId'])
    data_id = builder.CreateString(obj['dataId'])
    data_model = data_models.get(obj['dataModel'], None)
    start = obj['start']
    stop = obj['stop']

    uris = []
    uris_len = len(obj['uris'])
    for _uri in obj['uris']:
        _, idf_descriptor = SEAScope.types.idf_descriptor.serialize(builder,
                                                                    _uri)
        uris.append(idf_descriptor)
    cls.GranuleMetadataStartUrisVector(builder, uris_len)
    for i in uris[::-1]:
        builder.PrependUOffsetTRelative(i)
    _uris = builder.EndVector(uris_len)

    # optional attributes
    title = builder.CreateString(obj.get('title', ''))
    institution = builder.CreateString(obj.get('institution', ''))
    comment = builder.CreateString(obj.get('comment', ''))
    file_id = builder.CreateString(obj.get('file_id', ''))
    product_version = builder.CreateString(obj.get('product_version', ''))
    lat_min = obj.get('lat_min', 0.0)
    lat_max = obj.get('lat_max', 0.0)
    lon_min = obj.get('lon_min', 0.0)
    lon_max = obj.get('lon_max', 0.0)
    creator_email = builder.CreateString(obj.get('creator_email', ''))
    station_id = builder.CreateString(obj.get('station_id', ''))
    platform = builder.CreateString(obj.get('platform', ''))
    sensor = builder.CreateString(obj.get('sensor', ''))

    cls.GranuleMetadataStart(builder)
    cls.GranuleMetadataAddSourceId(builder, src_id)
    cls.GranuleMetadataAddCollectionId(builder, col_id)
    cls.GranuleMetadataAddGranuleId(builder, gra_id)
    cls.GranuleMetadataAddDataId(builder, data_id)
    cls.GranuleMetadataAddDataModel(builder, data_model)
    cls.GranuleMetadataAddStart(builder, start)
    cls.GranuleMetadataAddStop(builder, stop)
    cls.GranuleMetadataAddUris(builder, _uris)
    cls.GranuleMetadataAddHasTitle(builder, 'title' in obj)
    cls.GranuleMetadataAddHasInstitution(builder, 'institution' in obj)
    cls.GranuleMetadataAddHasComment(builder, 'comment' in obj)
    cls.GranuleMetadataAddHasFileId(builder, 'file_id' in obj)
    cls.GranuleMetadataAddHasProductVersion(builder, 'product_version' in obj)
    cls.GranuleMetadataAddHasLatMin(builder, 'lat_min' in obj)
    cls.GranuleMetadataAddHasLatMax(builder, 'lat_max' in obj)
    cls.GranuleMetadataAddHasLonMin(builder, 'lon_min' in obj)
    cls.GranuleMetadataAddHasLonMax(builder, 'lon_max' in obj)
    cls.GranuleMetadataAddHasCreatorEmail(builder, 'creator_email' in obj)
    cls.GranuleMetadataAddHasStationId(builder, 'station_id' in obj)
    cls.GranuleMetadataAddHasPlatform(builder, 'platform' in obj)
    cls.GranuleMetadataAddHasSensor(builder, 'sensor' in obj)
    cls.GranuleMetadataAddTitle(builder, title)
    cls.GranuleMetadataAddInstitution(builder, institution)
    cls.GranuleMetadataAddComment(builder, comment)
    cls.GranuleMetadataAddFileId(builder, file_id)
    cls.GranuleMetadataAddProductVersion(builder, product_version)
    cls.GranuleMetadataAddLatMin(builder, lat_min)
    cls.GranuleMetadataAddLatMax(builder, lat_max)
    cls.GranuleMetadataAddLonMin(builder, lon_min)
    cls.GranuleMetadataAddLonMax(builder, lon_max)
    cls.GranuleMetadataAddCreatorEmail(builder, creator_email)
    cls.GranuleMetadataAddStationId(builder, station_id)
    cls.GranuleMetadataAddPlatform(builder, platform)
    cls.GranuleMetadataAddSensor(builder, sensor)
    gm = cls.GranuleMetadataEnd(builder)
    return builder, gm


def deserialize(o):
    """
    Rebuild a granule metadata from a FlatBuffers buffer.

    Parameters
    ----------
    buf : bytearray
        The buffer which contains the granule metadata object serialized with
        FlatBuffers

    Returns
    -------
    dict
        The deserialized granule metadata object as a dictionary.
    """
    result = {}
    result['sourceId'] = o.SourceId()
    result['collectionId'] = o.CollectionId()
    result['granuleId'] = o.GranuleId()
    result['dataId'] = o.DataId()
    data_model = o.DataModel()
    for k, v in data_models.items():
        if v == data_model:
            result['dataModel'] = k
            break
    result['start'] = o.Start()
    result['stop'] = o.Stop()
    result['uris'] = []
    uris_count = o.UrisLength()
    for i in range(0, uris_count):
        u = SEAScope.types.idf_descriptor.deserialize(o.Uris(i))
        result['uris'].append(u)

    if o.HasTitle():
        result['title'] = o.Title()
    if o.HasInstitution():
        result['institution'] = o.Institution()
    if o.HasComment():
        result['comment'] = o.Comment()
    if o.HasFileId():
        result['file_id'] = o.FileId()
    if o.HasProductVersion():
        result['product_version'] = o.ProductVersion()
    if o.HasLatMin():
        result['lat_min'] = o.LatMin()
    if o.HasLatMax():
        result['lat_max'] = o.LatMax()
    if o.HasLonMin():
        result['lon_min'] = o.LonMin()
    if o.HasLonMax():
        result['lon_max'] = o.LonMax()
    if o.HasCreatorEmail():
        result['creator_email'] = o.CreatorEmail()
    if o.HasStationId():
        result['station_id'] = o.StationId()
    if o.HasPlatform():
        result['platform'] = o.Platform()
    if o.HasSensor():
        result['sensor'] = o.Sensor()
    return result
