"""
Quick test to check if requests library is available in Unreal Python
"""
import sys

print("=" * 60)
print("Testing Python Libraries in Unreal")
print("=" * 60)

# Test requests
try:
    import requests
    print("✓ 'requests' library is available")
    print(f"  Version: {requests.__version__}")
except ImportError:
    print("✗ 'requests' library is NOT available")
    print("  We'll need to use an alternative approach")

# Test json (should always be available)
try:
    import json
    print("✓ 'json' library is available")
except ImportError:
    print("✗ 'json' library is NOT available (unexpected)")

print("=" * 60)
