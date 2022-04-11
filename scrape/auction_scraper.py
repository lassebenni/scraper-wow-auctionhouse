import logging
from random import randint
from time import sleep
from typing import List
import pandas as pd
import requests  # type: ignore

from models.auction import Lot, Lots
from models.item import Item, Items
from models.media import Media, Medias
from scrape.item_scraper import ItemScraper
from scrape.lot_scraper import LotScraper
from scrape.media_scraper import MediaScraper
from utils.aws import S3Connector
from utils.utils import load_pickle, store_as_pickle

logger = logging.getLogger(__name__)


class AuctionScraper:
    def __init__(self, access_token: str, bucket: str):
        self.access_token = access_token
        self.s3_connector = S3Connector(bucket)

    def crawl(self, sample: int = 0):
        lots_scraper = LotScraper(self.access_token)
        self.lots: Lots = lots_scraper.crawl()
        logger.info(f"{len(self.lots.lots)} lots crawled..")

        self.item_ids = list({lot.item.id for lot in self.lots.lots})
        logger.info(f"{len(self.item_ids)} item ids found..")

        previous_items_id: List[int] = load_pickle("data/item_ids.pickle")
        print(f"Previous {len(previous_items_id)} item ids found")
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
        print(f"{len(item_ids)} item ids found")

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
                print(f"Item {i+1}/{len(item_ids)} crawled.")
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
            logger.info(f"Wrote to {path}")

        if self.items:
            df = pd.DataFrame.from_records(self.items.dict()["items"])
            path = self.s3_connector.create_parquet_path("items")
            self.s3_connector.write_parquet(df, path)
            logger.info(f"Wrote to {path}")

        if self.medias:
            df = pd.DataFrame.from_records(self.medias.dict()["media"])
            path = self.s3_connector.create_parquet_path("medias")
            self.s3_connector.write_parquet(df, path)
            logger.info(f"Wrote to {path}")
