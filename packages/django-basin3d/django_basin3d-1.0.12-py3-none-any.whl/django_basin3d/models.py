"""
`django_basin3d.models`
***********************

.. currentmodule:: django_basin3d.models

:synopsis: The BASIN-3D Models
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

"""
from __future__ import unicode_literals

from importlib import import_module

from django.db import models


class StringListField(models.TextField):
    """
    StringListField stored delimited strings in the database.

    :param: delimiter
    :type: str
    """

    def __init__(self, *args, **kwargs):
        self.delimiter = ","
        if "delimiter" in kwargs.keys():
            self.delimiter = kwargs["delimiter"]

        super(StringListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list) or isinstance(value, tuple):
            return value
        elif isinstance(value, str):
            return value.split(self.delimiter)

        raise ValueError("ListField must be delimited string")

    def get_prep_value(self, value):
        if value is None:
            return value
        else:
            return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_db_prep_value(value, None)


class DataSource(models.Model):
    """
    Data Source definition

    Attributes:
        - *id:* string (inherited)
        - *name:* string
        - *id_prefix:* string, prefix that is added to all data source ids
        - *plugin_module:*
        - *plugin_class:*
        - *credentials:*
        - *enabled:*

    """
    name = models.CharField(max_length=20, unique=True, blank=False)
    id_prefix = models.CharField(max_length=5, unique=True, blank=False)
    location = models.TextField(blank=True)
    plugin_module = models.TextField(blank=True)
    plugin_class = models.TextField(blank=True)

    class Meta:
        ordering = ['id_prefix']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSource %r>' % (self.name)

    def get_plugin(self):
        """
        Return the plugin class
        """

        module = import_module(self.plugin_module)
        plugin_class = getattr(module, self.plugin_class)
        from django_basin3d.catalog import CatalogDjango
        return plugin_class(CatalogDjango())


class ObservedProperty(models.Model):
    """
    Defining the properties being observed (measured).
    See https://github.com/BASIN-3D/basin3d/blob/main/basin3d/data/basin3d_observed_property_vocabulary.csv

    Fields:
        - *basin3d_vocab:* string, BASIN-3D observed property vocabulary
        - *full_name:* string, Description of observed property
        - *categories:* List of strings, categories (in order of priority), .
        - *units:* string, units of the observed property
    """

    basin3d_vocab = models.CharField(max_length=50, unique=True, blank=False, primary_key=True)
    full_name = models.CharField(max_length=255)
    categories = StringListField(blank=True, null=True)
    units = models.CharField(max_length=50, blank=False)

    class Meta:
        ordering = ('basin3d_vocab',)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.description

    def __repr__(self):
        return '<ObservedProperty %r>' % self.basin3d_vocab


class AttributeMapping(models.Model):
    """
    A data class for attribute mappings between datasource vocabularies and BASIN-3D vocabularies.
    These are the associations defined in the datasource (i.e., plugin) mapping file.

    Fields:
         - *attr_type:* Attribute Type; e.g., STATISTIC, RESULT_QUALITY, OBSERVED_PROPERTY; separate compound mappings with ':'
         - *basin3d_vocab:* The BASIN-3D vocabulary; separate compound mappings with ':'
         - *basin3d_desc:* The BASIN-3D vocabulary descriptions; objects or enum
         - *datasource_vocab:* The datasource vocabulary
         - *datasource_desc:* The datasource vocabulary description
         - *datasource:* The datasource of the mapping
    """

    attr_type = models.CharField(max_length=50)
    basin3d_vocab = models.CharField(max_length=50)
    basin3d_desc = models.JSONField()
    datasource_vocab = models.CharField(max_length=50, blank=False)
    datasource_desc = models.TextField(blank=True, null=True)
    datasource = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('datasource', 'attr_type', 'datasource_vocab')
        ordering = ('datasource', 'attr_type', 'basin3d_vocab')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.datasource_vocab
