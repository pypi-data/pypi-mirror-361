"""
OSM Data Client - A client for the HOTOSM Raw Data API.

This library provides tools for fetching OpenStreetMap data through the
Raw Data API provided by the Humanitarian OpenStreetMap Team (HOT).
"""

# import logging
# TODO why do we have this line?
# logging.getLogger(__name__).addHandler(logging.NullHandler())

from osm_data_client.exceptions import (
    OSMClientError,
    ValidationError,
    APIRequestError,
    TaskPollingError,
    DownloadError,
)

from osm_data_client.models import (
    GeometryInput,
    RequestParams,
    RawDataApiMetadata,
    AutoExtractOption,
    RawDataClientConfig,
    RawDataOutputOptions,
)
from osm_data_client.processing import RawDataResult
from osm_data_client.client import get_osm_data, RawDataClient, RawDataAPI

__version__ = "0.1.0"

__all__ = [
    # Core functions
    "get_osm_data",
    # Client classes
    "RawDataClient",
    "RawDataAPI",
    "AutoExtractOption",
    # Model classes
    "GeometryInput",
    "RequestParams",
    "RawDataApiMetadata",
    "RawDataClientConfig",
    "RawDataOutputOptions",
    "RawDataResult",
    # Exceptions
    "OSMClientError",
    "ValidationError",
    "APIRequestError",
    "TaskPollingError",
    "DownloadError",
]
