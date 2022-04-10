import logging
import requests  # type: ignore
import json

from models.auction import Lots

logger = logging.getLogger(__name__)


class LotScraper:
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

        return Lots(lots=response_json["auctions"])
