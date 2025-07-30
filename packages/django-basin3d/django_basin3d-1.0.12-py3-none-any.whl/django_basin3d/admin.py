from django_basin3d.models import AttributeMapping, DataSource, ObservedProperty
from django.contrib import admin
from django.contrib.admin import ModelAdmin


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin_module', 'plugin_class', 'location')
    fields = ('name', 'location', 'plugin_module', 'plugin_class', 'id_prefix',)
    readonly_fields = ('name', 'id_prefix', 'plugin_module', 'plugin_class')
    actions = None


@admin.register(ObservedProperty)
class ObservedPropertyAdmin(ModelAdmin):
    list_display = ('basin3d_vocab', 'full_name', 'categories', 'units')

    actions = None


@admin.register(AttributeMapping)
class AttributeMappingAdmin(ModelAdmin):
    list_display = ('attr_type', 'basin3d_vocab', 'basin3d_desc', 'datasource_vocab', 'datasource_desc', 'datasource')
