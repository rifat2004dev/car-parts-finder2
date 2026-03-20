from scraper.atlantic_auto_scraper import AtlanticAutoSparesScraper
from scraper.autozone_scraper import AutoZoneScraper
from scraper.berlin_car_parts_scraper import BerlinCarPartsScraper
from scraper.boss_autospares_scraper import BossAutoSparesScraper
from scraper.facebook_scraper import FacebookMarketplaceScraper
from scraper.gumtree_scraper import GumtreeScraper
from scraper.masterparts_scraper import MasterpartsScraper
from scraper.midas_scraper import MidasScraper
from scraper.modern_auto_parts_scraper import ModernAutoPartsScraper
from scraper.onlinecarparts_scraper import OnlineCarPartsScraper
from scraper.takealot_scraper import TakealotScraper

SCRAPER_REGISTRY = [
    GumtreeScraper,
    FacebookMarketplaceScraper,
    ModernAutoPartsScraper,
    BerlinCarPartsScraper,
    OnlineCarPartsScraper,
    TakealotScraper,
    AutoZoneScraper,
    MidasScraper,
    MasterpartsScraper,
    BossAutoSparesScraper,
    AtlanticAutoSparesScraper,
]

