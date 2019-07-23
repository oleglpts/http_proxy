import os
import pathlib
from pkg_resources import resource_string


def copy_config():
    files = {
        'data/config.json': 'config.json',
        'data/locale/ru/LC_MESSAGES/http_proxy.mo': 'locale/ru/LC_MESSAGES/http_proxy.mo',
    }
    for file_name in files:
        path = pathlib.Path('%s/.http_proxy' % os.getenv('HOME'), files[file_name])
        path.parent.mkdir(parents=True, exist_ok=True)
        text = resource_string(__name__, file_name)
        open(str(path), 'wb').write(text)
