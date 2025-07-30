"""
`django_basin3d.catalog`
************************

.. currentmodule:: django_basin3d.catalog

:synopsis: The Django BASIN-3D Catalog
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

"""
import importlib
import json
import logging
from typing import Iterator, List, Optional, Union

from django.conf import settings
from django.db import IntegrityError, OperationalError
from django.db.models import Q

from basin3d.core.catalog import CatalogBase, CatalogException
from basin3d.core.models import ObservedProperty, AttributeMapping
# from basin3d.core.plugin import PluginMount
from basin3d.core.schema.enum import BaseEnum, MappedAttributeEnum, MAPPING_DELIMITER, NO_MAPPING_TEXT, set_mapped_attribute_enum_type

logger = logging.getLogger(__name__)


class CatalogDjango(CatalogBase):

    def __init__(self, variable_filename: str = 'basin3d_observed_property_vocabulary.csv'):
        super().__init__(variable_filename)

    def is_initialized(self) -> bool:
        """Has the catalog been initialized?"""

        try:
            from django_basin3d.models import DataSource
            datasources = DataSource.objects.count()
            if isinstance(datasources, int):
                return datasources > 0
            logger.debug('Catalog not initialized')
            return False
        except ImportError:
            return False

    def _convert_django_observed_property(self, django_opv) -> Optional[ObservedProperty]:
        """
        Convert django observed property variable to basin3d
        :param django_opv:
        :return:
        """
        if django_opv:
            return ObservedProperty(
                basin3d_vocab=django_opv.basin3d_vocab,
                full_name=django_opv.full_name,
                categories=django_opv.categories.split(","),
                units=django_opv.units
            )
        return None

    def _convert_django_attribute_mapping(self, django_am) -> Optional[AttributeMapping]:
        """
        Convert django attribute_mapping
        :param django_am:
        :return:
        """
        if django_am:

            attr_type_list = django_am.attr_type.split(MAPPING_DELIMITER)

            if isinstance(django_am.basin3d_desc, list):
                basin3d_desc_list = django_am.basin3d_desc
            else:
                # It should always be a list
                try:
                    basin3d_desc_list = json.loads(django_am.basin3d_desc)
                except Exception as e:
                    raise e

            basin3d_desc = []

            for attr_type, desc in zip(attr_type_list, basin3d_desc_list):
                if attr_type == MappedAttributeEnum.OBSERVED_PROPERTY.value:
                    op = ObservedProperty(
                        basin3d_vocab=desc.get('basin3d_vocab'),
                        full_name=desc.get('full_name'),
                        categories=desc.get('categories'),
                        units=desc.get('units')
                    )
                    basin3d_desc.append(op)
                elif attr_type in MappedAttributeEnum.values():
                    attr_enum_class = set_mapped_attribute_enum_type(attr_type)
                    attr_type_enum = getattr(attr_enum_class, desc)
                    basin3d_desc.append(attr_type_enum)
                else:
                    basin3d_desc.append(desc)

            return AttributeMapping(
                attr_type=django_am.attr_type,
                basin3d_vocab=django_am.basin3d_vocab,
                basin3d_desc=basin3d_desc,
                datasource_vocab=django_am.datasource_vocab,
                datasource_desc=django_am.datasource_desc,
                datasource=django_am.datasource
            )

        return None

    def _convert_basin3d_attr_mapping_basin3d_desc(self, basin3d_desc: list) -> list:
        json_ready_basin3d_desc = []

        for desc in basin3d_desc:
            if isinstance(desc, ObservedProperty):
                json_ready_basin3d_desc.append(desc.to_dict())
            elif isinstance(desc, BaseEnum):
                json_ready_basin3d_desc.append(desc.value)
            else:
                json_ready_basin3d_desc.append(desc)

        return json_ready_basin3d_desc

    def _get_observed_property(self, basin3d_vocab) -> Optional[ObservedProperty]:
        """
        Access a single observed property variable

        :param basin3d_vocab: the observed property name
        :return:
        """
        from django_basin3d import models as django_models

        try:
            opv = django_models.ObservedProperty.objects.get(basin3d_vocab=basin3d_vocab)
            return self._convert_django_observed_property(opv)
        except django_models.ObservedProperty.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def _get_attribute_mapping(self, datasource_id, attr_type, basin3d_vocab, datasource_vocab, **kwargs) -> Optional[AttributeMapping]:
        """

        :param datasource_id:
        :param attr_type:
        :param basin3d_vocab:
        :param datasource_vocab:
        :param kwargs:
        :return:
        """
        if not self.is_initialized():
            raise CatalogException("Datasource catalog has not been initialized")

        from django_basin3d import models as django_models

        try:
            opv = django_models.AttributeMapping.objects.get(
                datasource__name=datasource_id, attr_type=attr_type, basin3d_vocab=basin3d_vocab, datasource_vocab=datasource_vocab)
            return self._convert_django_attribute_mapping(opv)
        except django_models.ObservedProperty.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def find_observed_property(self, basin3d_vocab) -> Optional[ObservedProperty]:
        """
                Return the :class:`basin3d.models.ObservedProperty` object for the BASIN-3D vocabulary specified.

                :param basin3d_vocab: BASIN-3D vocabulary
                :return: a :class:`basin3d.models.ObservedProperty` object
                """
        if not self.is_initialized():
            raise CatalogException("Datasource catalog has not been initialized")

        return self._get_observed_property(basin3d_vocab)

    def find_observed_properties(self, basin3d_vocab: Optional[List[str]] = None) -> Iterator[Optional[ObservedProperty]]:
        """
        Report the observed_properties available based on the BASIN-3D vocabularies specified. If no BASIN-3D vocabularies are specified, then return all observed properties available.

        :param basin3d_vocab: list of the BASIN-3D observed properties
        :return: generator that yields :class:`basin3d.models.ObservedProperty` objects
        """
        if not self.is_initialized():
            raise CatalogException("Datasource catalog has not been initialized")

        from django_basin3d import models as django_models

        if not basin3d_vocab:
            for opv in django_models.ObservedProperty.objects.all():
                yield self._convert_django_observed_property(opv)
        else:
            for b3d_vocab in basin3d_vocab:
                opv = self._get_observed_property(b3d_vocab)
                if opv is not None:
                    yield opv

    def find_datasource_attribute_mapping(self, datasource_id: str, attr_type: str, datasource_vocab: str) -> Optional[AttributeMapping]:
        if not self.is_initialized():
            raise CatalogException("Datasource catalog has not been initialized")

        # Consider checking args for a value

        from django_basin3d import models as django_models

        # Setup the search parameters
        query_params = {
            'datasource__name': datasource_id,
            'attr_type__contains': attr_type,
            'datasource_vocab': datasource_vocab
        }

        msg = (f'No mapping was found for attr: "{attr_type}" and for datasource vocab: "{datasource_vocab}" '
               f'in datasource: "{datasource_id}".')

        try:
            ds = django_models.DataSource.objects.get(name=datasource_id)
        except django_models.DataSource.DoesNotExist:
            msg = f'No Data Source "{datasource_id}" found.'
            ds = django_models.DataSource(name=None, location=None, id_prefix=None, plugin_module=None, plugin_class=None)
        except Exception as e:
            if e.__class__.__name__ not in ['DoesNotExist']:
                raise e

        # set up empty AttributeMapping in case where mapping is not found or another error occurs
        attr_mapping = AttributeMapping(attr_type=attr_type, basin3d_vocab=NO_MAPPING_TEXT, basin3d_desc=[],
                                        datasource_vocab=datasource_vocab, datasource_desc=msg, datasource=ds)

        try:
            attr_mapping = django_models.AttributeMapping.objects.get(**query_params)
        except django_models.AttributeMapping.DoesNotExist:
            return attr_mapping
        except django_models.AttributeMapping.MultipleObjectsReturned:
            msg = (f'Multiple mappings found for attr: "{attr_type}" and datasource vocab: "{datasource_vocab}" '
                   f'in datasource: "{datasource_id}". This should never happen.')
            attr_mapping.datasource_desc = msg
            return attr_mapping
        except Exception as e:
            if e.__class__.__name__ not in ['DoesNotExist', 'MultipleObjectsReturned']:
                raise e

        return self._convert_django_attribute_mapping(attr_mapping)

    def find_attribute_mappings(self, datasource_id: str = None, attr_type: str = None, attr_vocab: Union[str, List] = None,
                                from_basin3d: bool = False) -> Iterator[AttributeMapping]:

        if not self.is_initialized():
            raise CatalogException("Datasource catalog has not been initialized")

        def construct_attr_vocab_query(attr_vocab_list, is_from_basin3d):
            query = Q(_connector=Q.OR)
            for a_vocab in attr_vocab_list:
                if not is_from_basin3d:
                    query.add(('datasource_vocab__exact', a_vocab), conn_type=Q.OR)
                elif MAPPING_DELIMITER in a_vocab:
                    query.add(('basin3d_vocab__regex', a_vocab), conn_type=Q.OR)
                else:
                    query.add(('basin3d_vocab__exact', a_vocab), conn_type=Q.OR)
                    query.add(('basin3d_vocab__regex', f'.*:{a_vocab}'), conn_type=Q.OR)
                    query.add(('basin3d_vocab__regex', f'{a_vocab}:.*'), conn_type=Q.OR)
                    query.add(('basin3d_vocab__regex', f'.*:{a_vocab}:.*'), conn_type=Q.OR)
            return query

        from django_basin3d import models as django_models

        query_params = []

        if datasource_id is not None:
            try:
                django_models.DataSource.objects.get(name=datasource_id)
            except django_models.DataSource.DoesNotExist:
                logger.warning(f'No datasource for datasource_id {datasource_id} was found. Check plugin initialization')
                yield None
            except Exception as e:
                if e.__class__.__name__ not in ['DoesNotExist']:
                    raise CatalogException(e)

            query_params.append(Q(datasource__name=datasource_id))

        if attr_type is not None:
            if attr_type not in MappedAttributeEnum.values():
                logger.warning(f'Attribute type {attr_type} is invalid')
                yield None

            query_params.append(Q(attr_type__contains=attr_type))

        if attr_vocab:
            if isinstance(attr_vocab, str):
                attr_vocab = [attr_vocab]
            elif not isinstance(attr_vocab, List):
                raise CatalogException("attr_vocab must be a str or list")
            attr_vocab_query = construct_attr_vocab_query(attr_vocab, from_basin3d)
            query_params.append(attr_vocab_query)

        try:
            attr_mappings = django_models.AttributeMapping.objects.filter(*query_params)
        except django_models.AttributeMapping.DoesNotExist:
            vocab_source_type = 'datasource'
            if from_basin3d:
                vocab_source_type = 'BASIN-3D'
            logger.info(f'No mapping was found for attr: "{attr_type}" and for {vocab_source_type} vocab: "{attr_vocab}" '
                        f'in datasource: "{datasource_id}".')
            pass
        except Exception as e:
            if e.__class__.__name__ not in ['DoesNotExist']:
                raise e

        for attr_mapping in attr_mappings:
            yield self._convert_django_attribute_mapping(attr_mapping)

    def _init_catalog(self, **kwargs):
        """
        Initialize the catalog database

        :return:
        """
        if not self.is_initialized():
            from django_basin3d import models as django_models

            # Now create the Datasource objects in the data base
            from basin3d.core.plugin import PluginMount
            for name, plugin in PluginMount.plugins.items():
                module_name = plugin.__module__
                class_name = plugin.__name__

                logger.info("Loading Plugin = {}.{}".format(module_name, class_name))

                try:
                    datasource = django_models.DataSource.objects.get(name=plugin.get_meta().id)
                except django_models.DataSource.DoesNotExist:
                    logger.info("Registering NEW Data Source Plugin '{}.{}'".format(module_name, class_name))
                    datasource = django_models.DataSource()
                    if hasattr(plugin.get_meta(), "connection_class"):
                        datasource.credentials = plugin.get_meta().connection_class.get_credentials_format()

                # Update the datasource
                datasource.name = plugin.get_meta().id
                datasource.location = plugin.get_meta().location
                datasource.id_prefix = plugin.get_meta().id_prefix
                datasource.plugin_module = module_name
                datasource.plugin_class = class_name
                datasource.save()
                logger.info("Updated Data Source '{}'".format(plugin.get_meta().id))

    def _insert(self, record):
        """
        :param record:
        """
        from django_basin3d import models as django_models

        if self.is_initialized():
            if isinstance(record, ObservedProperty):
                try:
                    p = django_models.ObservedProperty()
                    p.basin3d_vocab = record.basin3d_vocab
                    p.full_name = record.full_name
                    p.categories = ",".join(record.categories)  # type: ignore
                    p.units = record.units
                    p.save()
                    logger.info(f'inserted {record.basin3d_vocab}')

                except IntegrityError as ie:
                    # This object has already been loaded
                    logger.debug(f'Integrity error for OP: {ie}')
                    pass

                except Exception as e:
                    logger.warning("Error Registering ObservedProperty '{}': {}".format(record.basin3d_vocab, str(e)))

            elif isinstance(record, AttributeMapping):
                try:
                    ds_name = django_models.DataSource.objects.get(name=record.datasource.id)

                    record_basin3d_desc = self._convert_basin3d_attr_mapping_basin3d_desc(record.basin3d_desc)

                    p = django_models.AttributeMapping()
                    p.datasource = ds_name
                    p.attr_type = record.attr_type
                    p.basin3d_vocab = record.basin3d_vocab
                    p.basin3d_desc = record_basin3d_desc
                    p.datasource_vocab = record.datasource_vocab
                    p.datasource_desc = record.datasource_desc
                    p.save()
                    logger.info(f'inserted {record.datasource_vocab} mapping attribute')

                except IntegrityError:
                    # This object has already been loaded
                    logger.info(f'Warning: skipping AttributeMapping "{record.basin3d_vocab}". Already loaded.')
                    pass

                except Exception as e:
                    logger.info(f'Error Registering AttributeMapping "{record.basin3d_vocab}": {str(e)}')
        else:
            raise CatalogException('Could not insert record. Catalog not initialize')


def load_data_sources(sender, **kwargs):
    """
    Load the Broker data sources from the registered plugins.

    :param sender:
    :param kwargs:
    :return:
    """
    # Load all the plugins found in apps
    from basin3d.core.plugin import PluginMount

    for django_app in settings.INSTALLED_APPS:
        try:
            importlib.import_module(f'{django_app}.plugins')
            logger.info(f'Loaded {django_app} plugins')

            plugins = kwargs.get('plugins')
            if not plugins:
                plugins = PluginMount.plugins.values()
                plugin_count = len(plugins)

            logger.info(f'Attempting to load {plugin_count} plugins for {django_app}.')
            catalog = CatalogDjango()
            catalog.initialize([v(catalog) for v in plugins])
        except ImportError as e:
            logger.warning(f'Warning: Potential error during attempt to import plugins for installed app: {e}. '
                           f'Please double check.')
            pass
        except OperationalError as oe:
            logger.error(f'Operational Error "{oe}" - Most likely happens on a reverse migration.')


def reload_data_sources(sender, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """
    from django_basin3d import models as django_models

    try:
        django_models.AttributeMapping.objects.all().delete()
        logger.info('Attribute Mappings entries deleted.')
        django_models.ObservedProperty.objects.all().delete()
        logger.info('Observed Properties entries deleted.')
        django_models.DataSource.objects.all().delete()
        logger.info('Data Source entries deleted.')

        load_data_sources(sender, **kwargs)
        attribute_mapping_count = django_models.AttributeMapping.objects.count()
        observed_property_count = django_models.ObservedProperty.objects.count()
        datasource_count = django_models.DataSource.objects.count()
        logger.info(f'Data sources reloaded: data sources = {datasource_count}, '
                    f'observed properties = {observed_property_count}, '
                    f'attribute mappings = {attribute_mapping_count}')

    except CatalogException as e:
        logger.error(f'Error reloading data sources: {e}')
