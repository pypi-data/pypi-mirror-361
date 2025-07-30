"""
========
REST API
========
.. currentmodule:: django_basin3d

:platform: Unix, Mac
:synopsis: All BASIN-3D REST API calls are read-only (GET). The browsable API may be accessed at the root URL of the application.
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top


Synthesis API
*************
Synthesis is the process of converting multiple heterogeneous data sources into a single uniform format.
This section describes BASIN-3D synthesis REST API.

Data Sources
------------
BASIN-3D Data sources definitions.  All data sources defined are available for synthesis in the
subsequent APIs.

| `/datasources --` Returns a list of data sources
| `/datasources/:id_prefix --` Get a single data source

**Attributes:**
    - *name:* Unique name for the data source
    - *id_prefix:* A unique iset of characters to prefix ids for the data source
    - *location:* Location of the data source
    - *observed_property:* BASIN-3D Observed Property mappings for the data source

**URLs**
  + url -- URL with details for the data source
  + check -- Validation URL for the data source connection


Observed Property
---------------------------
BASIN-3D vocabulary for observed properties. A observed property defines what is
being measured. Data source vocabularies are mapped to these BASIN-3D vocabularies.

| `/observedproperty --` Returns a list of observed properties
| `/observedproperty/:basin3d_vocab --` Get a single observed property

**Attributes:**
    - *basin3d_vocab:* Unique observed property vocabulary
    - *full_name:* Descriptive name for the observed property
    - *categories:* Categories of which the variable is a member, listed in hierarchical order
    - *units:* Units of the observed property

**URLs**
  + url -- URL with details for the observed property


Attribute Mapping
-------------------
The Attribute Mappings registered for the Data Source plugins

| `/attributemapping --` Returns a list of all attribute mappings
| `/attributemapping/:id --` Get a single attribute mapping

**Attributes:**
    - *attr_type:* Attribute Type; e.g., STATISTIC, RESULT_QUALITY, OBSERVED_PROPERTY; separate compound mappings with ':'
    - *basin3d_vocab:* The BASIN-3D vocabulary; separate compound mappings with ':'
    - *basin3d_desc:* The BASIN-3D vocabulary descriptions; observed property objects or enum
    - *datasource_vocab:* The datasource vocabulary
    - *datasource_desc:* The datasource vocabulary description
    - *datasource:* The datasource of the mapping

**URLs**
  + url -- URL with details for the attribute mapping


Monitoring Features
-------------------
A feature on which an observation is made. Features organized into spatial
hierarchies are described via the related_sampling_feature complex

| `/monitoringfeature --` Returns a list of monitoring features types
| `/monitoringfeature/:featuretype --` Returns a list of monitoring features of the specified feature type
| `/monitoringfeature/:featuretype/:id --` Get a single monitoring feature

**Synthesis Response**
This endpoint returns the following synthesis response object.

```json
{ "query": {}, "data": [] }
```

**Data Attributes**
    Attribute for each data element from the synthesis response is as follows:

    - *id:* Unique feature identifier
    - *name:* Feature name
    - *description:* Description of the feature
    - *feature_type:* Type of feature, supported feature types: REGION, SUBREGION, BASIN, SUBBASIN, WATERSHED, SUBWATERSHED, SITE, PLOT, HORIZONTAL PATH, VERTICAL PATH, POINT
    - *observed_property_variables:* list of observed variables made at the feature. Observed property variables are configured via the plugins.
    - *related_sampling_feature_complex:* List of related sampling_features. PARENT features are currently supported.
    - *shape:* Shape of the feature: POINT, CURVE, SURFACE, SOLID
    - *coordinates:* Location of feature in absolute and/or representative datum
    - *description_reference:* Additional information about the feature
    - *related_party:* List of people or organizations responsible for the feature
    - *utc_offset:* Coordinate Universal Time offset in hours

**URLs**
  + url -- URL with details for the feature


MeasurementTimeseriesTVPObservation
-----------------------------------
MeasurementTimeseriesTVPObservation: Series of measurement (numerical) observations
in TVP (time value pair) format grouped by time (i.e., a timeseries).
Attributes specified at the group level apply to all observations.

| `/measurementtvptimeseries/?filters --` Get a single measurement timeseries TVP observation:

**Synthesis Response**
This endpoint returns the following synthesis response object.

```json
{ "query": {}, "data": [] }
```

**Data Attributes**
    Attribute for each data element from the synthesis response is as follows:

    * *id:* Observation identifier (optional)
    * *type:* MEASUREMENT_TVP_TIMESERIES
    * *observed_property:* BASIN-3D vocabulary for the observation's observed property
    * *sampling_medium:* Sampling medium of the observed property (SOLID_PHASE, WATER, GAS, OTHER)
    * *phenomenon_time:* datetime of the observation, for a timeseries the start and end times can be provided
    * *utc_offset:* Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    * *feature_of_interest:* feature on which the observation is being made
    * *feature_of_interest_type:* feature type of the feature of interest
    * *result:* values = the observed values of the observed property being assessed, and result_qualit (opt) = their result_quality,
    * *time_reference_position:* position of timestamp in aggregated_duration (START, MIDDLE, END)
    * *aggregation_duration:* time period represented by observation (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
    * *unit_of_measurement:* units in which the observation is reported
    * *statistic:* statistical property of the observation result (MEAN, MIN, MAX, TOTAL)
    * *result_quality:* quality assessments of the results (VALIDATED, UNVALIDATED, SUSPECTED, REJECTED, ESTIMATED)

**URLs**
  + url -- URL with details for the feature
  + datasource -- URL of the datasource

**Filters**
    - *monitoring_feature (required):* comma separated list of monitoring_features ids
    - *observed_property (required):* comma separated list of observed property basin3d vocabularies
    - *start_date (required):* date YYYY-MM-DD
    - *end_date (optional):* date YYYY-MM-DD
    - *aggregation_duration (default: DAY):* enum (YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|NONE)
    - *statistic (optional):* comma separated list of statistic enum(s) (MEAN|MIN|MAX|INSTANTANEOUS)
    - *result_quality (optional):* comma separated list of result quality enum(s) enum (VALIDATED|UNVALIDATED|SUSPECTED|REJECTED|ESTIMATED)
    - *sampling_medium (optional):* comma separated list of sampling medium enum(s) (SOLID_PHASE|WATER|GAS|OTHER)
    - *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)

"""
from importlib.metadata import version, PackageNotFoundError
import logging

logger = logging.getLogger(__name__)

try:
    __version__ = version("django_basin3d")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ['get_url']

# application loads this AppConfig subclass by default
# when django_basin3d is added to INSTALLED_APPS
default_app_config = 'django_basin3d.apps.Basin3DConfig'


def __insert_basin3d_defaults():
    """
    Insert BASIN-3D default settings :class:`django_basin3d.settings`
    """

    from django.conf import global_settings, settings
    from django_basin3d import settings as basin3d_settings

    # Add the values from the application.settings module
    for key in dir(basin3d_settings):
        if key.isupper():

            # Add the defaults to the global setting
            setattr(global_settings, key, getattr(basin3d_settings, key))

            # only add default if they have not been set already
            # We don't want to override local setting
            if not hasattr(settings, key):
                setattr(settings, key, getattr(basin3d_settings, key))
            elif key in ['BASIN3D', 'REST_FRAMEWORK']:
                basin3d = getattr(basin3d_settings, key)
                local_basin3d = getattr(settings, key)
                for key in basin3d.keys():
                    if key not in local_basin3d:
                        local_basin3d[key] = basin3d[key]


__insert_basin3d_defaults()


def get_url(url, params=None, headers=None, verify=False):
    """
    Send a GET request to the specified URL

    :param url:
    :param params: request parameters
    :param headers: request headers
    :param verify: verify SSL connection
    :return: Response
    """
    import requests
    response = requests.get(url, params=params, verify=verify, headers=headers)
    logger.debug("url:{}".format(response.url))
    return response


def post_url(url, params=None, headers=None, verify=False):
    """
    Send a POST request to the specified URL

    :param url:
    :param params: request parameters
    :param headers: request headers
    :param verify: verify SSL connection
    :return: Response
    """
    import requests
    response = requests.post(url, params=params, verify=verify, headers=headers)
    logger.debug("url:{}".format(response.url))
    return response


__all__ = ['synthesis']
