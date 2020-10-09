import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))
sys.path.insert(0, os.path.join(BASE_DIR, 'toutiao'))
print(sys.path)

from toutiao import create_app
from settings.default import DefaultConfig

app = create_app(DefaultConfig, enable_config_file=True)


@app.route('/')
def route_map():
    return "hello"
