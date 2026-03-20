from .gumtree_scraper import search_gumtree
from .midas_scraper import search_midas
from .masterparts_scraper import search_masterparts
from .modern_auto_parts_scraper import search_modern

SCRAPER_REGISTRY = [
    search_gumtree,
    search_midas,
    search_masterparts,
    search_modern
]
