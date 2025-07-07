BATCH_SIZE = 4
BUFFER_SIZE = 10000
API_KEY=""
GEMINI_API_KEY=""

try:
    from settings_local import *
    print("Loaded local overrides from settings_local.py")
except ImportError:
    print("No settings_local.py found, using default settings.")