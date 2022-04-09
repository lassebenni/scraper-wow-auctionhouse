import os
from scrape.auction_scraper import AuctionScraper


def main():
    access_token = os.environ.get("BLIZZARD_ACCESS_TOKEN")
    scraper = AuctionScraper(access_token)
    scraper.crawl()
    scraper.crawl_items(5)


if __name__ == "__main__":
    main()
