"""
Lync Attribution Client

Main client for server-side attribution tracking.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests

from .exceptions import LyncAPIError, LyncConfigurationError
from .types import EventType, TrackingData, DeviceInfo
from .utils import generate_device_fingerprint


class Lync:
    """
    Lync Attribution Client
    
    Server-side attribution tracking for Python applications.
    Track conversions, analyze attribution, and match server events
    to original web clicks or mobile app installs.
    """
    
    def __init__(
        self,
        api_base_url: str,
        entity_id: str,
        api_key: Optional[str] = None,
        debug: bool = False,
        timeout: float = 30.0,
        retries: int = 3
    ):
        """
        Initialize Lync Attribution client.
        
        Args:
            api_base_url: Your Lync instance URL (e.g., "https://api.lync.so")
            entity_id: Your entity/organization ID
            api_key: API key for authentication (optional for some endpoints)
            debug: Enable debug logging
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
        """
        if not api_base_url:
            raise LyncConfigurationError("api_base_url is required")
        if not entity_id:
            raise LyncConfigurationError("entity_id is required")
            
        self.api_base_url = api_base_url.rstrip('/')
        self.entity_id = entity_id
        self.api_key = api_key
        self.debug = debug
        self.timeout = timeout
        self.retries = retries
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Lync-Python/1.0.0',
            'Content-Type': 'application/json'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
            
        if debug:
            print(f"🐍 Lync Python SDK initialized")
            print(f"📍 API URL: {self.api_base_url}")
            print(f"🏢 Entity ID: {self.entity_id}")
    
    @classmethod
    def from_env(cls, debug: bool = False) -> 'Lync':
        """
        Create Lync client from environment variables.
        
        Expected environment variables:
        - LYNC_API_BASE_URL: Your Lync instance URL
        - LYNC_ENTITY_ID: Your entity/organization ID  
        - LYNC_API_KEY: API key for authentication (optional)
        - LYNC_DEBUG: Enable debug logging (optional, "true"/"false")
        
        Args:
            debug: Override debug setting from environment
            
        Returns:
            Configured Lync client
            
        Raises:
            LyncConfigurationError: If required environment variables are missing
        """
        import os
        
        api_base_url = os.getenv('LYNC_API_BASE_URL')
        if not api_base_url:
            raise LyncConfigurationError("LYNC_API_BASE_URL environment variable is required")
            
        entity_id = os.getenv('LYNC_ENTITY_ID')
        if not entity_id:
            raise LyncConfigurationError("LYNC_ENTITY_ID environment variable is required")
            
        api_key = os.getenv('LYNC_API_KEY')
        env_debug = os.getenv('LYNC_DEBUG', '').lower() == 'true'
        
        return cls(
            api_base_url=api_base_url,
            entity_id=entity_id,
            api_key=api_key,
            debug=debug or env_debug
        )
    
    def track_conversion(
        self,
        event_name: str,
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        click_id: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Track a conversion event.
        
        Args:
            event_name: Name of the conversion event (e.g., "signup", "purchase")
            customer_id: Unique customer identifier
            customer_email: Customer email address
            click_id: Original click ID from web attribution
            custom_properties: Additional custom data
            device_info: Device information (auto-detected if not provided)
            
        Returns:
            API response data
        """
        return self.track_event(
            event_type=EventType.CONVERSION,
            event_name=event_name,
            customer_id=customer_id,
            customer_email=customer_email,
            click_id=click_id,
            custom_properties=custom_properties,
            device_info=device_info
        )
    
    def track_click(
        self,
        link_id: str,
        click_id: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Track a link click event.
        
        Args:
            link_id: Identifier for the link that was clicked
            click_id: Custom click ID (auto-generated if not provided)
            custom_properties: Additional custom data
            device_info: Device information
            
        Returns:
            API response data including generated click_id
        """
        if not click_id:
            click_id = self._generate_click_id()
            
        return self.track_event(
            event_type=EventType.CLICK,
            event_name="Link Click",
            click_id=click_id,
            custom_properties={
                "link_id": link_id,
                **(custom_properties or {})
            },
            device_info=device_info
        )
    
    def track_event(
        self,
        event_type: EventType,
        event_name: str,
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        click_id: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Track a custom event.
        
        Args:
            event_type: Type of event (click, conversion, custom)
            event_name: Name of the event
            customer_id: Unique customer identifier
            customer_email: Customer email address
            click_id: Original click ID for attribution
            custom_properties: Additional custom data
            device_info: Device information
            
        Returns:
            API response data
        """
        # Auto-detect device info if not provided
        if device_info is None:
            device_info = self._get_server_device_info()
        
        # Build payload
        payload = {
            "entity_id": self.entity_id,
            "event_type": event_type.value,
            "event_name": event_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_info": device_info.to_dict() if device_info else {},
        }
        
        # Add optional fields
        if customer_id:
            payload["customer_id"] = customer_id
        if customer_email:
            payload["customer_email"] = customer_email
        if click_id:
            payload["click_id"] = click_id
        if custom_properties:
            payload["custom_properties"] = custom_properties
            
        # Send event
        return self._send_request("/api/track/server", payload)
    
    def get_attribution(
        self,
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        click_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get attribution data for a customer or click.
        
        Args:
            customer_id: Customer identifier
            customer_email: Customer email
            click_id: Original click ID
            
        Returns:
            Attribution data and confidence scores
        """
        params = {}
        if customer_id:
            params["customer_id"] = customer_id
        if customer_email:
            params["customer_email"] = customer_email
        if click_id:
            params["click_id"] = click_id
            
        if not params:
            raise LyncConfigurationError("At least one identifier required")
            
        return self._send_request("/api/attribution", method="GET", params=params)
    
    def generate_fingerprint(self, device_info: Optional[DeviceInfo] = None) -> str:
        """
        Generate cross-platform device fingerprint.
        
        Args:
            device_info: Device information (auto-detected if not provided)
            
        Returns:
            Device fingerprint string compatible with web/mobile SDKs
        """
        if device_info is None:
            device_info = self._get_server_device_info()
            
        return generate_device_fingerprint(device_info)
    
    def _get_server_device_info(self) -> DeviceInfo:
        """Get server-side device information."""
        import platform
        import socket
        
        return DeviceInfo(
            platform="server",
            device_type="server",
            os_name=platform.system(),
            os_version=platform.release(),
            python_version=platform.python_version(),
            hostname=socket.gethostname(),
            timezone=time.tzname[0] if time.tzname else "UTC",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _generate_click_id(self) -> str:
        """Generate unique click ID."""
        timestamp = int(time.time() * 1000)
        random_part = str(uuid.uuid4()).replace('-', '')[:8]
        return f"click_{timestamp}_{random_part}"
    
    def _send_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send HTTP request to Lync API.
        
        Args:
            endpoint: API endpoint path
            data: Request payload for POST/PUT
            method: HTTP method
            params: Query parameters for GET
            
        Returns:
            Parsed JSON response
            
        Raises:
            LyncAPIError: When API returns an error
        """
        url = urljoin(self.api_base_url, endpoint.lstrip('/'))
        
        # Prepare request kwargs
        kwargs = {
            'timeout': self.timeout,
            'params': params
        }
        
        if data and method in ['POST', 'PUT', 'PATCH']:
            kwargs['json'] = data
        
        if self.debug:
            print(f"📤 {method} {url}")
            if data:
                print(f"📦 Payload: {json.dumps(data, indent=2)}")
        
        # Send request with retries
        last_exception = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                
                if self.debug:
                    print(f"📥 Response: {response.status_code}")
                    if response.text:
                        print(f"📦 Data: {response.text}")
                
                # Handle response
                if response.ok:
                    try:
                        return response.json()
                    except ValueError:
                        return {"success": True, "message": "OK"}
                else:
                    # Try to get error message from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', response.text)
                    except ValueError:
                        error_message = response.text or f"HTTP {response.status_code}"
                    
                    raise LyncAPIError(
                        message=error_message,
                        status_code=response.status_code,
                        response_data=error_data if 'error_data' in locals() else None
                    )
                    
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    if self.debug:
                        print(f"🔄 Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    break
        
        # All retries failed
        if last_exception:
            raise LyncAPIError(f"Request failed after {self.retries + 1} attempts: {last_exception}")
        else:
            raise LyncAPIError("Request failed for unknown reason")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close() 