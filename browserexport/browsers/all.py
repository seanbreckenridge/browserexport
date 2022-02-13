from typing import List, Type
from .common import Browser
from .firefox import Firefox
from .waterfox import Waterfox
from .palemoon import Palemoon
from .chrome import Chrome
from .chromium import Chromium
from .brave import Brave
from .safari import Safari
from .vivaldi import Vivaldi
from .firefox_mobile import FirefoxMobile
from .firefox_mobile_legacy import FirefoxMobileLegacy

# As this is a namespace package, you're free to add additional files
# to this package in a separate directory, and then append them (or override this file, by
# placing your namespace package before this on your PYTHONPATH),
# to this list, and they'd be added to the global list in the rest of the library
#
# for more information, see:
# https://www.python.org/dev/peps/pep-0420/#dynamic-path-computation
# https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages
# https://packaging.python.org/guides/packaging-namespace-packages/
# https://github.com/seanbreckenridge/reorder_editable

DEFAULT_BROWSERS: List[Type[Browser]] = [
    Chrome,
    Firefox,
    Safari,
    Brave,
    Waterfox,
    Chromium,
    Vivaldi,
    Palemoon,  # has to be after waterfox/firefox derivates, else it could be mis-detected
    FirefoxMobile,
    FirefoxMobileLegacy,
]
