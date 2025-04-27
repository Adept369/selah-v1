# orchestrator/conftest.py

import sys
import os

# Prepend the `app/` folder so `import app.*` always works under pytest
here = os.path.dirname(__file__)
app_path = os.path.join(here, "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)
