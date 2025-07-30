"""
Utility functions for Lync Attribution Python SDK.
"""

import hashlib
import platform
import time
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse

from .types import DeviceInfo


def generate_device_fingerprint(device_info: DeviceInfo) -> str:
    """
    Generate a cross-platform device fingerprint compatible with web/mobile SDKs.
    
    Args:
        device_info: Device information
        
    Returns:
        Device fingerprint string in format: "key:value;key:value;..."
    """
    # Build fingerprint components (server-specific)
    components = [
        f"device:{device_info.device_type or 'server'}",
        f"platform:{device_info.platform or 'server'}",
    ]
    
    if device_info.os_name:
        components.append(f"os:{device_info.os_name}")
    if device_info.os_version:
        components.append(f"os_version:{device_info.os_version}")
    if device_info.hostname:
        # Use a hash of hostname for privacy
        hostname_hash = hashlib.md5(device_info.hostname.encode()).hexdigest()[:8]
        components.append(f"host:{hostname_hash}")
    if device_info.timezone:
        components.append(f"tz:{device_info.timezone}")
    if device_info.language:
        components.append(f"lang:{device_info.language}")
    if device_info.region:
        components.append(f"region:{device_info.region}")
    
    return ";".join(sorted(components))


def generate_server_fingerprint() -> str:
    """
    Generate a server-specific fingerprint for the current environment.
    
    Returns:
        Server fingerprint string
    """
    device_info = DeviceInfo(
        platform="server",
        device_type="server",
        os_name=platform.system(),
        os_version=platform.release(),
        python_version=platform.python_version(),
        timezone=time.tzname[0] if time.tzname else "UTC"
    )
    return generate_device_fingerprint(device_info)


def extract_click_id_from_url(url: str) -> Optional[str]:
    """
    Extract click_id parameter from a URL.
    
    Args:
        url: URL to parse
        
    Returns:
        Click ID if found, None otherwise
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        click_ids = params.get('click_id', [])
        return click_ids[0] if click_ids else None
    except Exception:
        return None


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email appears valid
    """
    if not email or '@' not in email:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
        
    local, domain = parts
    return len(local) > 0 and len(domain) > 0 and '.' in domain


def sanitize_custom_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize custom properties for API submission.
    
    Args:
        properties: Raw custom properties
        
    Returns:
        Sanitized properties dictionary
    """
    if not properties:
        return {}
    
    sanitized = {}
    
    for key, value in properties.items():
        # Ensure key is string and not empty
        if not isinstance(key, str) or not key.strip():
            continue
            
        # Sanitize key (remove special characters)
        clean_key = ''.join(c for c in key if c.isalnum() or c in '_-.')
        if not clean_key:
            continue
            
        # Handle different value types
        if value is None:
            sanitized[clean_key] = None
        elif isinstance(value, (str, int, float, bool)):
            sanitized[clean_key] = value
        elif isinstance(value, (list, dict)):
            # Convert complex types to strings
            sanitized[clean_key] = str(value)
        else:
            # Convert other types to string
            sanitized[clean_key] = str(value)
    
    return sanitized


def create_event_id() -> str:
    """
    Create a unique event ID.
    
    Returns:
        Unique event identifier
    """
    import uuid
    return str(uuid.uuid4())


def get_user_agent_info(user_agent: str) -> Dict[str, Any]:
    """
    Parse user agent string for device information.
    
    Args:
        user_agent: HTTP User-Agent header value
        
    Returns:
        Parsed user agent information
    """
    if not user_agent:
        return {}
    
    info = {
        "raw": user_agent,
        "platform": "unknown",
        "device_type": "unknown",
        "browser": "unknown"
    }
    
    ua_lower = user_agent.lower()
    
    # Detect platform
    if "windows" in ua_lower:
        info["platform"] = "windows"
    elif "mac" in ua_lower or "darwin" in ua_lower:
        info["platform"] = "macos"
    elif "linux" in ua_lower:
        info["platform"] = "linux"
    elif "android" in ua_lower:
        info["platform"] = "android"
    elif "ios" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
        info["platform"] = "ios"
    
    # Detect device type
    if "mobile" in ua_lower or "phone" in ua_lower:
        info["device_type"] = "mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        info["device_type"] = "tablet"
    else:
        info["device_type"] = "desktop"
    
    # Detect browser
    if "chrome" in ua_lower:
        info["browser"] = "chrome"
    elif "firefox" in ua_lower:
        info["browser"] = "firefox"
    elif "safari" in ua_lower:
        info["browser"] = "safari"
    elif "edge" in ua_lower:
        info["browser"] = "edge"
    
    return info 