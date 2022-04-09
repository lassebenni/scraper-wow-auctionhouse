import logging
import pickle
from random import randint
from typing import List
import requests  # type: ignore
import json

from models.auction import Lot, Lots
from models.item import Item, Items
from models.media import Media, Medias
from scrape.item_scraper import ItemScraper
from scrape.media_scraper import MediaScraper

logger = logging.getLogger(__name__)


class AuctionScraper:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def crawl(self) -> Lots:
        url = f"https://us.api.blizzard.com/data/wow/connected-realm/60/auctions?namespace=dynamic-us&locale=en_US&access_token={self.access_token}"

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
            "X-Requested-With": "XMLHttpRequest",
        }

        logger.info("Crawling auctions.")
        response = requests.request("GET", url, headers=headers)
        response_json = json.loads(response.text)
        self.lots = Lots(lots=response_json["auctions"])
        logger.info(f"{len(self.lots.lots)} lots crawled..")
        self.item_ids = list({lot.item.id for lot in self.lots.lots})
        logger.info(f"{len(self.item_ids)} item ids found..")
        self._write_json("data/auctions.json")
        logger.info(f"Written to auctions.json")

    def crawl_items(self, sample: int = 0):
        previous_items_id: List[int] = self._load_item_ids()
        item_ids = [
            item_id for item_id in self.item_ids if item_id not in previous_items_id
        ]
        if sample > 0:
            sample_item_ids = []
            for _ in range(sample):
                rand_item_id = randint(0, len(item_ids) - 1)
                sample_item_ids.append(rand_item_id)
            item_ids = sample_item_ids

        logger.info(f"{len(item_ids)} item ids found. Crawling items..")

        item_scraper = ItemScraper(self.access_token)
        media_scraper = MediaScraper(self.access_token)

        handled_items: List[Item] = []
        handled_media: List[Media] = []
        try:
            logger.info(f"Crawling {len(item_ids)}")
            for i, item_id in enumerate(item_ids):
                item: Item = item_scraper.crawl(item_id)
                handled_items.append(item)
                media: Media = media_scraper.crawl(item_id)
                handled_media.append(media)
                previous_items_id.append(item_id)
                logger.info(f"Item {i+1}/{len(item_ids)} crawled.")
        except Exception as e:
            logger.error(e)
            logger.info("Storing processed item_ids.")
            self._store_item_ids(previous_items_id)

        items = Items(items=handled_items)
        medias = Medias(media=handled_media)

        logger.info("Writing items.json")
        item_scraper.write_json(items, "data/items.json")
        logger.info("Writing items_media.json")
        media_scraper.write_json(medias, "data/items_media.json")

    def _store_item_ids(self, item_ids: List[int]):
        with open("data/item_ids.pickle", "wb") as f:
            pickle.dump(item_ids, f)

    def _write_json(self, path: str):
        with open(path, "w") as f:
            f.write(self.lots.json())

    def random_lots(self, size: int = 1) -> Lots:
        sample_lots: List[Lot] = []
        for _ in range(size):
            random_lot: Lot = self.lots.lots[randint(0, len(self.lots.lots))]
            sample_lots.append(random_lot)

        return sample_lots

    def _load_item_ids(self) -> List[int]:
        with open("data/item_ids.pickle", "rb") as f:
            return pickle.load(f)
