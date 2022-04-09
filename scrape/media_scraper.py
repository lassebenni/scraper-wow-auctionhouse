import logging
import requests  # type: ignore
import json

from models.media import Media, Medias

logger = logging.getLogger(__name__)


class MediaScraper:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def crawl(self, item_id: int) -> Media:
        url = f"https://us.api.blizzard.com/data/wow/media/item/{item_id}?namespace=static-9.2.0_42277-us&locale=en_US&access_token={self.access_token}"

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

        try:
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                response_json = json.loads(response.text)
                media = Media(**response_json)
            else:
                logger.info(
                    f"Error while crawling item {item_id}: {response.status_code} {response.text}"
                )
        except Exception as e:
            logger.error(f"Error while crawling item {item_id}: {e}")

        return media

    def write_json(self, medias: Medias, path: str):
        with open(path, "w") as f:
            f.write(medias.json())
