__author__ = "Ze Yang"
__contact__ = "yangze1995007@163.com"
__license__ = "MIT"
__version__ = "2.2.3"
__date__ = "2025-07-10"


try:
    from importlib.metadata import version
except Exception:
    try:
        from importlib_metadata import version
    except Exception:
        pass

try:
    __version__ = version("ion_CSP")
except Exception:
    pass
