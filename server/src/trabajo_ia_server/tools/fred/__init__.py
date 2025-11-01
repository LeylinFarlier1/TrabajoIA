"""
FRED (Federal Reserve Economic Data) tools.

Tools for interacting with the FRED API.
"""
from trabajo_ia_server.tools.fred.search_series import search_fred_series
from trabajo_ia_server.tools.fred.get_tags import get_fred_tags
from trabajo_ia_server.tools.fred.related_tags import search_fred_related_tags
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags
from trabajo_ia_server.tools.fred.search_series_tags import search_series_tags
from trabajo_ia_server.tools.fred.search_series_related_tags import search_series_related_tags
from trabajo_ia_server.tools.fred.get_series_tags import get_series_tags
from trabajo_ia_server.tools.fred.observations import get_series_observations
from trabajo_ia_server.tools.fred.category import get_category
from trabajo_ia_server.tools.fred.category_children import get_category_children
from trabajo_ia_server.tools.fred.category_related import get_category_related
from trabajo_ia_server.tools.fred.category_series import get_category_series
from trabajo_ia_server.tools.fred.category_tags import get_category_tags
from trabajo_ia_server.tools.fred.category_related_tags import get_category_related_tags

__all__ = [
    "search_fred_series",
    "get_fred_tags",
    "search_fred_related_tags",
    "get_series_by_tags",
    "search_series_tags",
    "search_series_related_tags",
    "get_series_tags",
    "get_series_observations",
    "get_category",
    "get_category_children",
    "get_category_related",
    "get_category_series",
    "get_category_tags",
    "get_category_related_tags",
]
