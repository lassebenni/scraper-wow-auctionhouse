import os
from scrape.auction_scraper import AuctionScraper


def main():
    access_token = os.environ.get("BLIZZARD_ACCESS_TOKEN")
    bucket = os.environ.get("AWS_S3_BUCKET")
    scraper = AuctionScraper(access_token, bucket=bucket)
    scraper.crawl()


if __name__ == "__main__":
    main()
