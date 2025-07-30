"""
`django_basin3d.synthesis`
**************************

.. currentmodule:: django_basin3d.synthesis

:synopsis: The high level BASIN-3D synthesis models.
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>
:module author: Charuleka Varadharajan <cvaradharajan@lbl.gov>


* :py:mod:`~django_basin3d.synthesis.serializers` - Serializers that render :py:mod:`basin3d.core.models` from Python objects to `JSON` and back again.
* :py:mod:`~django_basin3d.synthesis.viewsets` - Controllers for BASIN-3D REST api

"""
from . import serializers

__all__ = ['serializers']
