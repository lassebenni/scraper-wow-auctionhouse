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

logger = logging.getLogger(__name__)


class AuctionScraper:
    def __init__(self, access_token: str, bucket: str):
        self.access_token = access_token
        self.s3_connector = S3Connector(bucket)

    def crawl(self, sample: int = 0):
        lots_scraper = LotScraper(self.access_token)
        lots: Lots = lots_scraper.crawl()

        if lots:
            df = pd.DataFrame.from_records(lots.dict()["lots"])
            path = self.s3_connector.create_parquet_path("lots")
            self.s3_connector.write_parquet(df, path)
            logger.info(f"Wrote to {path}")

        logger.info(f"{len(lots.lots)} lots crawled..")

        self.item_ids = list({lot.item.id for lot in lots.lots})
        logger.info(f"{len(self.item_ids)} item ids found..")

        scraped_item_ids: List[int] = self.read_item_ids()
        print(f"Previous {len(scraped_item_ids)} item ids found")
        item_ids = [
            item_id for item_id in self.item_ids if item_id not in scraped_item_ids
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
                scraped_item_ids.append(item_id)
                logger.info(f"Item {i+1}/{len(item_ids)} crawled.")
                print(f"Item {i+1}/{len(item_ids)} crawled.")

                # write intermediate hanlded item_ids to s3 in case of failure
                if (i + 1) % 100 == 0:
                    items = Items(items=handled_items)
                    df_items = pd.DataFrame.from_records(items.dict()["items"])
                    self.write_to_s3(df_items, "items")
                    medias = Medias(media=handled_media)
                    df_media = pd.DataFrame.from_records(medias.dict()["media"])
                    self.write_to_s3(df_media, "media")
                    self.write_item_ids(scraped_item_ids)

                    # clear handled items
                    handled_items = []
                    handled_media = []
        except Exception as e:
            logger.error(e)
            logger.info("Storing processed item_ids.")

    def random_lots(self, lots: List[Lot], size: int = 1) -> Lots:
        sample_lots: List[Lot] = []
        for _ in range(size):
            random_lot: Lot = lots[randint(0, len(lots))]
            sample_lots.append(random_lot)

        return sample_lots

    def write_to_s3(self, df: pd.DataFrame, name: str):
        path = self.s3_connector.create_parquet_path(name)
        self.s3_connector.write_parquet(df, path)
        logger.info(f"Wrote to {path}")

    def read_item_ids(self) -> List[int]:
        df = self.s3_connector.read_csv("item_ids.csv")
        return list(df["id"].values)

    def write_item_ids(self, item_ids: List[int]) -> pd.DataFrame:
        df = pd.DataFrame(item_ids, columns=["id"])
        self.s3_connector.write_csv(df, "item_ids.csv")
