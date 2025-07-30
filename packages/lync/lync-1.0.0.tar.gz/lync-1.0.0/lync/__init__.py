"""
Lync Attribution Python SDK

Cross-platform attribution tracking that connects web clicks to mobile app events.

Usage:
    >>> from lync import Lync
    >>> 
    >>> # Initialize
    >>> lync = Lync(
    ...     api_base_url="https://api.lync.so",
    ...     entity_id="your-entity-id",
    ...     api_key="your-api-key"
    ... )
    >>> 
    >>> # Track server-side events
    >>> lync.track_conversion(
    ...     event_name="signup",
    ...     customer_id="user-123",
    ...     custom_properties={"plan": "premium"}
    ... )
"""

from .client import Lync
from .exceptions import LyncError, LyncAPIError, LyncConfigurationError
from .types import EventType, DeviceInfo, TrackingData

__version__ = "1.0.0"
__author__ = "Lync.so"
__email__ = "support@lync.so"
__license__ = "MIT"

__all__ = [
    "Lync",
    "LyncError", 
    "LyncAPIError",
    "LyncConfigurationError",
    "EventType",
    "DeviceInfo", 
    "TrackingData",
] 