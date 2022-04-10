import logging
from random import randint
from time import sleep
from typing import List
import pandas as pd
import requests  # type: ignore
import json

from models.auction import Lot, Lots
from models.item import Item, Items
from models.media import Media, Medias
from scrape.item_scraper import ItemScraper
from scrape.media_scraper import MediaScraper
from utils.aws import S3Connector
from utils.utils import load_pickle, store_as_pickle

logger = logging.getLogger(__name__)


class AuctionScraper:
    def __init__(self, access_token: str, bucket: str):
        self.access_token = access_token
        self.s3_connector = S3Connector(bucket)

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

        logger.info(f"Written to auctions.json")

    def crawl_items(self, sample: int = 0):
        previous_items_id: List[int] = load_pickle("data/item_ids.pickle")
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
                sleep(1)
                if item:
                    handled_items.append(item)
                media: Media = media_scraper.crawl(item_id)
                sleep(1)
                if media:
                    handled_media.append(media)
                previous_items_id.append(item_id)
                logger.info(f"Item {i+1}/{len(item_ids)} crawled.")
        except Exception as e:
            logger.error(e)
            logger.info("Storing processed item_ids.")
            store_as_pickle(previous_items_id, "data/item_ids.pickle")

        self.items = Items(items=handled_items)
        self.medias = Medias(media=handled_media)

    def random_lots(self, size: int = 1) -> Lots:
        sample_lots: List[Lot] = []
        for _ in range(size):
            random_lot: Lot = self.lots.lots[randint(0, len(self.lots.lots))]
            sample_lots.append(random_lot)

        return sample_lots

    def write_to_s3(self):
        if self.lots:
            df = pd.DataFrame.from_records(self.lots.dict()["lots"])
            path = self.s3_connector.create_parquet_path("lots")
            self.s3_connector.write_parquet(df, path)

        if self.items:
            df = pd.DataFrame.from_records(self.items.dict()["items"])
            path = self.s3_connector.create_parquet_path("items")
            self.s3_connector.write_parquet(df, path)

        if self.medias:
            df = pd.DataFrame.from_records(self.medias.dict()["media"])
            path = self.s3_connector.create_parquet_path("medias")
            self.s3_connector.write_parquet(df, path)
