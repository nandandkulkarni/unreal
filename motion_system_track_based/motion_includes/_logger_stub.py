# Simple inline logger functions for motion_includes
# This avoids import conflicts with other logger modules in the Python path

def log(message, log_file=None):
    """Print message"""
    print(message)

def log_header(title):
    """Print header"""
    print("=" * 60)
    print(title)
    print("=" * 60)
