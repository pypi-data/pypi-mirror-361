"""
Command Line Interface for Lync Attribution Python SDK.
"""

import argparse
import json
import sys
from typing import Dict, Any

from .client import Lync
from .exceptions import LyncError
from .utils import generate_server_fingerprint


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lync Attribution Python SDK CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track a conversion
  lync track-conversion signup --customer-id user123 --api-url https://api.lync.so --entity-id my-org

  # Generate server fingerprint
  lync fingerprint

  # Test API connection
  lync test --api-url https://api.lync.so --entity-id my-org --api-key your-key
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Common arguments
    def add_common_args(subparser):
        subparser.add_argument('--api-url', required=True, help='Lync API base URL')
        subparser.add_argument('--entity-id', required=True, help='Your entity ID')
        subparser.add_argument('--api-key', help='API key for authentication')
        subparser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    # Track conversion command
    track_parser = subparsers.add_parser('track-conversion', help='Track a conversion event')
    add_common_args(track_parser)
    track_parser.add_argument('event_name', help='Name of the conversion event')
    track_parser.add_argument('--customer-id', help='Customer identifier')
    track_parser.add_argument('--customer-email', help='Customer email')
    track_parser.add_argument('--click-id', help='Original click ID')
    track_parser.add_argument('--properties', help='Custom properties as JSON string')
    
    # Test connection command
    test_parser = subparsers.add_parser('test', help='Test API connection')
    add_common_args(test_parser)
    
    # Generate fingerprint command
    fingerprint_parser = subparsers.add_parser('fingerprint', help='Generate server fingerprint')
    fingerprint_parser.add_argument('--format', choices=['simple', 'json'], default='simple',
                                   help='Output format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'fingerprint':
            return cmd_fingerprint(args)
        elif args.command == 'test':
            return cmd_test(args)
        elif args.command == 'track-conversion':
            return cmd_track_conversion(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
            
    except LyncError as e:
        print(f"Lync Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.debug if hasattr(args, 'debug') else False:
            import traceback
            traceback.print_exc()
        return 1


def cmd_fingerprint(args) -> int:
    """Generate server fingerprint command."""
    fingerprint = generate_server_fingerprint()
    
    if args.format == 'json':
        output = {
            "fingerprint": fingerprint,
            "type": "server"
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Server Fingerprint: {fingerprint}")
    
    return 0


def cmd_test(args) -> int:
    """Test API connection command."""
    print("🔗 Testing Lync API connection...")
    
    with Lync(
        api_base_url=args.api_url,
        entity_id=args.entity_id,
        api_key=args.api_key,
        debug=args.debug
    ) as client:
        # Try to track a test event
        from .types import EventType
        result = client.track_event(
            event_type=EventType.CUSTOM,
            event_name="CLI Test",
            custom_properties={"source": "cli", "test": True}
        )
        
        print("✅ Connection successful!")
        if args.debug:
            print(f"Response: {json.dumps(result, indent=2)}")
    
    return 0


def cmd_track_conversion(args) -> int:
    """Track conversion command."""
    custom_properties = None
    if args.properties:
        try:
            custom_properties = json.loads(args.properties)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in --properties: {e}", file=sys.stderr)
            return 1
    
    with Lync(
        api_base_url=args.api_url,
        entity_id=args.entity_id,
        api_key=args.api_key,
        debug=args.debug
    ) as client:
        result = client.track_conversion(
            event_name=args.event_name,
            customer_id=args.customer_id,
            customer_email=args.customer_email,
            click_id=args.click_id,
            custom_properties=custom_properties
        )
        
        print(f"✅ Conversion '{args.event_name}' tracked successfully!")
        if args.debug:
            print(f"Response: {json.dumps(result, indent=2)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 