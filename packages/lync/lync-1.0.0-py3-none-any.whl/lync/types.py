"""
Type definitions for Lync Attribution Python SDK.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional, Union


class EventType(Enum):
    """Event types for attribution tracking."""
    CLICK = "click"
    CONVERSION = "conversion" 
    CUSTOM = "custom"
    INSTALL = "install"
    REGISTRATION = "registration"


@dataclass
class DeviceInfo:
    """Device information for attribution fingerprinting."""
    platform: str = "server"
    device_type: str = "server"
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    python_version: Optional[str] = None
    hostname: Optional[str] = None
    timezone: Optional[str] = None
    timestamp: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass 
class TrackingData:
    """Data structure for tracking events."""
    event_type: EventType
    event_name: str
    customer_id: Optional[str] = None
    customer_email: Optional[str] = None
    click_id: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None
    device_info: Optional[DeviceInfo] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API payload."""
        data = {
            "event_type": self.event_type.value,
            "event_name": self.event_name
        }
        
        if self.customer_id:
            data["customer_id"] = self.customer_id
        if self.customer_email:
            data["customer_email"] = self.customer_email  
        if self.click_id:
            data["click_id"] = self.click_id
        if self.custom_properties:
            data["custom_properties"] = self.custom_properties
        if self.device_info:
            data["device_info"] = self.device_info.to_dict()
            
        return data


@dataclass
class AttributionResult:
    """Result from attribution analysis."""
    matched: bool
    confidence: float
    attribution_type: str  # "direct", "probabilistic", "fallback"
    original_click_id: Optional[str] = None
    click_timestamp: Optional[str] = None
    conversion_timestamp: Optional[str] = None
    time_to_conversion: Optional[float] = None  # seconds
    campaign_data: Optional[Dict[str, Any]] = None
    device_match_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# Type aliases for common use cases
EventData = Dict[str, Any]
AttributionData = Dict[str, Any]
CustomProperties = Dict[str, Union[str, int, float, bool, None]] 