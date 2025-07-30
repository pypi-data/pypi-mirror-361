"""

.. currentmodule:: django_basin3d.serializers

:platform: Unix, Mac
:synopsis: BASIN-3D Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

About Django Serializers:

    Serializers allow complex data such as querysets and model instances to be converted
    to native Python datatypes that can then be easily rendered into JSON, XML or other
    content types. Serializers also provide deserialization, allowing parsed data to be
    converted back into complex types, after first validating the incoming data.
    https://www.django-rest-framework.org/api-guide/serializers/
"""
from django_basin3d.models import DataSource, ObservedProperty, AttributeMapping
from rest_framework.reverse import reverse
from rest_framework import serializers


class ChooseFieldsSerializerMixin(object):
    """
    A serializer that dynamically sets fields
    """

    def __init__(self, *args, **kwargs):

        # Instantiate the serializer superclass
        super(ChooseFieldsSerializerMixin, self).__init__(*args, **kwargs)

        if 'request' in self.context:  # type: ignore
            self.handle_fields(self.context['request'])  # type: ignore

    def handle_fields(self, request=None):
        """
        Restrict the fields by those in the request
        :param request:
        :return:
        """
        if request:
            fields = request.query_params.get('fields')
            if fields and len(fields) > 0:
                field_set = set(fields.split(","))

                # Remove the fields not in the intersection
                for field in set(self.fields.keys()).difference(field_set):  # type: ignore
                    self.fields.pop(field)  # type: ignore


class DelimitedListField(serializers.ListField):
    """
    Convert a delimited string field to a list
    """

    child = serializers.CharField()

    def __init__(self, *args, delimiter=",", **kwargs):
        super(DelimitedListField, self).__init__(*args, **kwargs)
        self.delimiter = delimiter

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        data_values = data.split(self.delimiter)
        return [self.child.to_representation(item) if item is not None else None for item in
                data_values]


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Data Source serializer that converts a models.DataSource
    """

    url = serializers.SerializerMethodField()
    attribute_mapping = serializers.SerializerMethodField()
    observed_property = serializers.SerializerMethodField()
    check = serializers.SerializerMethodField()

    def get_url(self, obj):
        """

        :param obj:
        :return:
        """
        url_kwargs = {'id_prefix': obj.id_prefix, }
        return "{}".format(reverse('datasource-detail', kwargs=url_kwargs, request=self.context["request"], ))

    def get_attribute_mapping(self, obj):
        """
        Return the url for the attribute mapping associated with the current datasource
        :param obj:
        :return:
        """
        format = None
        if "format" in self.context["request"].query_params:
            format = self.context["request"].query_params["format"]

        url_kwargs = {"id_prefix": obj.id_prefix, }

        return reverse("{}-attribute-mapping".format(obj.__class__.__name__.lower()), kwargs=url_kwargs,
                       request=self.context["request"], format=format)

    def get_observed_property(self, obj):
        """
        Return the url for the observed property associated with the current datasource
        :param obj:
        :return:
        """
        format = None
        if "format" in self.context["request"].query_params:
            format = self.context["request"].query_params["format"]

        url_kwargs = {"id_prefix": obj.id_prefix, }

        return reverse("{}-observed-property".format(obj.__class__.__name__.lower()), kwargs=url_kwargs,
                       request=self.context["request"], format=format)

    def get_check(self, obj):
        """
        Check the data source
        :param obj:
        :return:
        """
        url_kwargs = {'id_prefix': obj.id_prefix, }
        return "{}check/".format(reverse('datasource-detail', kwargs=url_kwargs, request=self.context["request"], ))

    class Meta:
        model = DataSource
        depth = 1
        fields = ('url', 'name', 'location', 'id_prefix',
                  'attribute_mapping', 'observed_property', 'check')
        read_only_fields = ('name', 'location', 'id_prefix',
                            'attribute_mapping', 'observed_property', 'check')
        lookup_field = 'name'


class ObservedPropertySerializer(serializers.HyperlinkedModelSerializer):
    """
    Observed Property Serializer
    """

    categories = DelimitedListField()

    def get_categories(self, obj):
        return obj.categories

    class Meta:
        model = ObservedProperty
        depth = 2
        fields = ('url', 'basin3d_vocab', 'full_name', 'categories', 'units')


class AttributeMappingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Attribute Mapping Serializer
    """

    datasource = serializers.SerializerMethodField()
    basin3d_desc = serializers.SerializerMethodField()

    def get_datasource(self, obj):
        """
        Return the url for the data sources associated with the current variable
        :param obj:
        :return:
        """
        url_kwargs = {'id_prefix': obj.datasource.id_prefix, }
        return "{}".format(reverse('datasource-detail', kwargs=url_kwargs, request=self.context["request"], ))

    def get_basin3d_desc(self, obj):
        """
        Return a list of str for enum and url for observed properties
        :param obj:
        :return:
        """
        return obj.basin3d_desc

    class Meta:
        model = AttributeMapping
        depth = 2
        fields = ('url', 'attr_type', 'basin3d_vocab', 'basin3d_desc', 'datasource_vocab', 'datasource_desc', 'datasource')
