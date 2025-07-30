"""
`django_basin3d.viewsets`
*************************

.. currentmodule:: django_basin3d.viewsets

:platform: Unix, Mac
:synopsis: BASIN-3D ViewSets
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top


"""
import django_filters
from rest_framework.decorators import action

from basin3d.core.schema.enum import MAPPING_DELIMITER, MappedAttributeEnum
from django_basin3d import get_url
from django_basin3d.models import AttributeMapping, DataSource, ObservedProperty
from django_basin3d.serializers import DataSourceSerializer, ObservedPropertySerializer, AttributeMappingSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of all Data Sources available to the BASIN-3D service

        **Properties**

        * *url:* url, Endpoint for Data Source
        * *name:* string, Unique name for the Data Source
        * *location:* string, Location of the Data Source
        * *id_prefix:* string, unique id prefix for all Data Source ids
        * *attribute_mapping:* url, List of Attribute Mappings that are mapped for Data Source
        * *observed_property:* url, List of Observed Properties that are mapped for Data Source
        * *check:* url, Validate the Data Source connection

    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    lookup_field = 'id_prefix'

    @action(detail=True)
    def check(self, request, id_prefix=None):
        """
        Determine if Data Source is available
        :param request:
        :param id_prefix:
        :return:
        """

        datasource = self.get_object()

        plugin = datasource.get_plugin()

        if hasattr(plugin.get_meta(), "connection_class"):
            http_auth = plugin.get_meta().connection_class(datasource)

            try:
                http_auth.login()
                return Response(data={"message": "Login to {} data source was successful".format(datasource.name),
                                      "success": True},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"message": str(e), "success": False},
                                status=status.HTTP_200_OK)

            finally:
                http_auth.logout()
        else:
            try:
                response = get_url("{}".format(datasource.location))

                if response.status_code == status.HTTP_200_OK:
                    return Response(
                        data={"message": "Response from {} data source was successful".format(datasource.name),
                              "success": True},
                        status=status.HTTP_200_OK)
                else:
                    return Response(
                        data={
                            "message": "Response from {} data source returns HTTP status {}".format(datasource.name,
                                                                                                    response.status_code),
                            "success": True},
                        status=status.HTTP_200_OK)

            except Exception as e:
                return Response(data={"message": str(e), "success": False},
                                status=status.HTTP_200_OK)

    @action(detail=True)  # Custom Route for an association
    def attribute_mapping(self, request, id_prefix=None):
        """
        Retrieve the Attribute Mappings for a Data Source.

        Maps to /datasource/{id_prefix}/attributemapping/

        :param request:
        :param id_prefix:
        :return:
        """
        params = AttributeMapping.objects.filter(datasource__id_prefix=id_prefix)

        # `HyperlinkedRelatedField` req:w
        # uires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = AttributeMappingSerializer(params, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True)  # Custom Route for an association
    def observed_property(self, request, id_prefix=None):
        """
        Retrieve the Observed Properties mapped for the current Data Source.

        Maps to /datasource/{id_prefix}/observedproperty/

        :param request:
        :param id_prefix:
        :return:
        """
        op_name = MappedAttributeEnum.OBSERVED_PROPERTY.value
        params = AttributeMapping.objects.filter(datasource__id_prefix=id_prefix, attr_type__contains=op_name)
        v = []
        for am in params:
            attr_type_list = am.attr_type.split(MAPPING_DELIMITER)
            vocab_list = am.basin3d_vocab.split(MAPPING_DELIMITER)
            for attr, vocab in zip(attr_type_list, vocab_list):
                if attr == op_name:
                    v.append(ObservedProperty.objects.get(pk=vocab))

        # `HyperlinkedRelatedField` requires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = ObservedPropertySerializer(v, many=True, context={'request': request})
        return Response(serializer.data)


class AttributeMappingViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of the Attribute Mappings for the registered Data Sources.

        **Properties**

        * *url:* url, endpoint for Attribute Mapping
        * *attr_type:* string, attribute mapping type
        * *basin3d_vocab:* string, observed property vocabulary
        * *basin3d_desc:* list, Observed Property (dict) or enum (str)
        * *datasource_vocab:* string, datasource vocabulary
        * *datasource_desc:* string, datasource description
        * *datasource:* string, data source defining the observed property

    """
    queryset = AttributeMapping.objects.all()
    serializer_class = AttributeMappingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)


class ObservedPropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of available BASIN-3D Observed Properties

        **Properties**

        * *url:* url, Endpoint for the observed property vocabulary
        * *basin3d_vocab:* string, Unique BASIN-3D observed property vocabulary
        * *full_name:* string, Descriptive name
        * *categories:* list of strings, Categories of which the variable is a member, listed in hierarchical order
        * *units:* string, units

    """
    queryset = ObservedProperty.objects.all()
    serializer_class = ObservedPropertySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
