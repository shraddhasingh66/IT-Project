"""
EasyCart Application Root Entry Point.
Delegates to the application located in Backend/app.py.
"""
import sys
import os

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_dir, "app.py"))
backend_module = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_module
spec.loader.exec_module(backend_module)

app = backend_module.app
get_db = getattr(backend_module, 'get_db', None)
init_db = getattr(backend_module, 'init_db', None)

if __name__ == '__main__':
    app.run(debug=True)
