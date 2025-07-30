"""
`django_basin3d.synthesis.viewsets`
***********************************

.. currentmodule:: django_basin3d.synthesis.viewsets

:synopsis: BASIN-3D Synthesis Model Viewsets (View Controllers) that support the REST API
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

"""
import logging
import pydantic
import typing
from basin3d.core.schema.enum import FeatureTypeEnum
from basin3d.core.schema.query import QueryMeasurementTimeseriesTVP, QueryMonitoringFeature
from rest_framework import status, versioning
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from basin3d.core.models import MeasurementTimeseriesTVPObservation, MonitoringFeature
from basin3d.core.synthesis import DataSourceModelAccess, MeasurementTimeseriesTVPObservationAccess, \
    MonitoringFeatureAccess

from django_basin3d.models import DataSource
from django_basin3d.synthesis.serializers import MeasurementTimeseriesTVPObservationSerializer, \
    MonitoringFeatureSerializer

logger = logging.getLogger(__name__)


def _get_request_feature_type(request):
    """
    Return the feature type if exists in the request
    :param request: request
    otherwise return the text version
    :return: the feature_type in the format specified, None if none exists
    """
    for feature_type in FeatureTypeEnum.values():
        urlpath = request.path_info
        url_feature_type = ''.join(feature_type.lower().split('_'))
        if f'{url_feature_type}s' in urlpath.split('/'):
            return feature_type
    return None


def _convert_str_params_to_list(params: dict, query_class) -> dict:
    """

    :param params:
    :param query_class:
    :return:
    """
    query_arg_types = typing.get_type_hints(query_class)

    for arg, arg_type in query_arg_types.items():
        # arg_type_str = str(arg_type)
        if 'List' not in str(arg_type) or arg not in params.keys():
            continue
        params[arg] = params[arg].split(',')

    return params


class DataSourcePluginViewSet(ViewSet, DataSourceModelAccess):
    """
    Base ViewsSet for all DataSource plugins.  This class extends the
    `Django Rest Framework <https://www.django-rest-framework.org/>`_
    class :class:`rest_framework.viewsets.ViewSet`. These are based on `Django generic views
    <https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/>`_.

    """
    versioning_class = versioning.NamespaceVersioning

    def __init__(self):
        # Override super class
        from django_basin3d.catalog import CatalogDjango
        self._catalog = CatalogDjango()

    @property
    def plugins(self):
        plugins = {}
        for d in DataSource.objects.all():
            plugins[d.id_prefix] = d.get_plugin()
        return plugins

    @property
    def catalog(self):
        return self._catalog

    def list(self, **kwargs) -> Response:
        """
        Return the synthesized plugin results

        :param request: The incoming request object
        :type request: :class:`rest_framework.request.Request`
        :param format: The format to present the data (default is json)
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """
        items = []

        request = kwargs['request']
        query = kwargs['query']

        itr = super(DataSourcePluginViewSet, self).list(query=query)
        for i in itr:
            items.append(i)

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        synthesis_response = itr.synthesis_response.dict(exclude_unset=True)
        synthesis_response['data'] = serializer.data
        return Response(synthesis_response)

    def retrieve(self, **kwargs) -> Response:
        """
        Retrieve a single object

        :param pk: The primary key
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """

        request = kwargs['request']
        query = kwargs['query']
        pk = kwargs['pk']

        try:
            item_synthesis_response = super(DataSourcePluginViewSet, self).retrieve(query)

            if not item_synthesis_response or not item_synthesis_response.data:
                return Response({"success": False, "detail": f"There is no detail for {pk}"},
                                status=status.HTTP_404_NOT_FOUND)
            else:

                try:
                    serializer = self.__class__.serializer_class(item_synthesis_response.data, context={'request': request})
                    synthesis_response = item_synthesis_response.dict(exclude_unset=True)
                    synthesis_response['data'] = serializer.data
                    return Response(synthesis_response)
                except Exception as e:
                    logger.error("Plugin error: {}".format(e))

        except Exception as e:
            return Response({'success': False, 'detail': str(e)},
                            status=status.HTTP_404_NOT_FOUND, )


class MonitoringFeatureViewSet(DataSourcePluginViewSet, MonitoringFeatureAccess):
    """
    MonitoringFeature: A feature upon which monitoring is made. OGC Timeseries Profile OM_MonitoringFeature.

    **Synthesis Response**
    This endpoint returns the following synthesis response object.

    ```json
    { "query": {}, "data": [] }
    ```

    **Data Attributes**
    Attribute for each data element from the synthesis response is as follows:

    * *id:* string, Unique feature identifier
    * *name:* string, Feature name
    * *description:* string, Description of the feature
    * *feature_type:* sting, FeatureType: REGION, SUBREGION, BASIN, SUBBASIN, WATERSHED, SUBWATERSHED, SITE, PLOT, HORIZONTAL PATH, VERTICAL PATH, POINT
    * *observed_properties:* list of observed variables made at the feature. Observed property variables are configured via the plugins.
    * *related_sampling_feature_complex:* list of related_sampling features. PARENT features are currently supported.
    * *shape:* string, Shape of the feature: POINT, CURVE, SURFACE, SOLID
    * *coordinates:* location of feature in absolute and/or representative datum
    * *description_reference:* string, additional information about the Feature
    * *related_party:* (optional) list of people or organizations responsible for the Feature
    * *utc_offset:* float, Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    * *url:* url, URL with details for the feature

    **Filter** by the following attributes (/?attribute=parameter&attribute=parameter&...)

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)
    * *parent_feature (optional):* a monitoring feature name

    **Restrict fields**  with query parameter `fields`. (e.g. `?fields=id,name`)
    """
    serializer_class = MonitoringFeatureSerializer
    synthesis_model = MonitoringFeature

    @typing.no_type_check
    def list(self, request: Request, format: str = None) -> Response:
        if not request:
            raise Response({"success": False, "detail": "Request is missing"}, status=status.HTTP_400_BAD_REQUEST)

        feature_type = _get_request_feature_type(request)

        params = request.query_params.dict()
        params = _convert_str_params_to_list(params, QueryMonitoringFeature)

        return super().list(request=request, format=format, query=QueryMonitoringFeature(feature_type=feature_type,
                                                                                         **params))

    @typing.no_type_check
    def retrieve(self, request: Request, pk: str) -> Response:
        if not request:
            return Response({'success': False, 'detail': "Request is missing"},
                            status=status.HTTP_400_BAD_REQUEST, )

        feature_type = _get_request_feature_type(request)

        # retrieve method order: MonitoringFeatureViewSet, DataSourceViewSet, MonitoringFeatureAccess
        # call super force this order based on inherited class ordering
        return super().retrieve(request=request, query=QueryMonitoringFeature(id=pk, feature_type=feature_type), pk=pk)

    @action(detail=True, url_name='regions-detail')
    def regions(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subregions-detail')
    def subregions(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='basins-detail')
    def basins(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subbasins-detail')
    def subbasins(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='watersheds-detail')
    def watersheds(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subwatersheds-detail')
    def subwatersheds(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='sites-detail')
    def sites(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='plots-detail')
    def plots(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='horizontalpaths-detail')
    def horizontalpaths(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='verticalpaths-detail')
    def verticalpaths(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='points-detail')
    def points(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)


class MeasurementTimeseriesTVPObservationViewSet(DataSourcePluginViewSet, MeasurementTimeseriesTVPObservationAccess):
    """
    MeasurementTimeseriesTVPObservation: Series of measurement (numerical) observations in
    TVP (time value pair) format grouped by time (i.e., a timeseries).

    **Synthesis Response**
    This endpoint returns the following synthesis response object.

    ```json
    { "query": {}, "data": [] }
    ```

    **Data Attributes**
    Attribute for each data element from the synthesis response is as follows:

    * *id:* string, Observation identifier (optional)
    * *type:* enum, MEASUREMENT_TVP_TIMESERIES
    * *observed_property:* str, BASIN-3D vocabulary for the observation's observed property
    * *datasource:* URL, url of the datasource
    * *sampling_medium:* enum, sampling medium of the observed property (SOLID_PHASE, WATER, GAS, OTHER)
    * *phenomenon_time:* datetime, datetime of the observation, for a timeseries the start and end times can be provided
    * *utc_offset:* float, Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    * *feature_of_interest:* MonitoringFeature obj, feature on which the observation is being made
    * *feature_of_interest_type:* enum (FeatureTypes), feature type of the feature of interest
    * *result:* dict of corresponding lists of TimeValuePairs, the observed values of the observed property being assessed, and (opt) their result_quality,
    * *time_reference_position:* enum, position of timestamp in aggregated_duration (START, MIDDLE, END)
    * *aggregation_duration:* enum, time period represented by observation (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
    * *unit_of_measurement:* string, units in which the observation is reported
    * *statistic:* enum, statistical property of the observation result (MEAN, MIN, MAX, TOTAL)
    * *result_quality:* list of enum, quality assessment of the result enum (VALIDATED, UNVALIDATED, SUSPECTED, REJECTED, ESTIMATED)

    **Filter** by the following attributes (?attribute=parameter,parameter&attribute=parameter&...):

    * *monitoring_feature (required):* comma separated list of monitoring_features ids
    * *observed_property (required):* comma separated list of observed property basin3d vocabularies
    * *start_date (required):* date YYYY-MM-DD
    * *end_date (optional):* date YYYY-MM-DD
    * *aggregation_duration (default: DAY):* enum (YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|NONE)
    * *statistic (optional):* comma separated list of statistic enum(s) (MEAN|MIN|MAX|INSTANTANEOUS)
    * *result_quality (optional):* comma separated list of result quality enum(s) enum (VALIDATED|UNVALIDATED|SUSPECTED|REJECTED|ESTIMATED)
    * *sampling_medium (optional):* comma separated list of sampling medium enum(s) (SOLID_PHASE|WATER|GAS|OTHER)
    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)

    **Restrict fields** with query parameter `fields`. (e.g. `?fields=id,name`)

    """
    serializer_class = MeasurementTimeseriesTVPObservationSerializer
    synthesis_model = MeasurementTimeseriesTVPObservation

    @action(detail=False, url_path='measurement_tvp_timeseries', url_name='measurementtvptimeseries-list', methods=['GET'])
    def list(self, request: Request, format: str = None) -> Response:
        if not request:
            return Response({'success': False, 'detail': "Request is missing"},
                            status=status.HTTP_400_BAD_REQUEST, )

        params = request.query_params.dict()
        params = _convert_str_params_to_list(params, QueryMeasurementTimeseriesTVP)

        try:
            return super().list(request=request, format=format, query=QueryMeasurementTimeseriesTVP(**params))
        except pydantic.ValidationError as exec_info:
            return Response({'success': False, 'detail': "Missing or invalid search criteria",
                             "errors": exec_info.errors()},
                            status=status.HTTP_400_BAD_REQUEST, )
