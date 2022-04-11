import awswrangler as wr
import pandas as pd
from datetime import datetime


class S3Connector:
    def __init__(self, bucket: str):
        self.bucket = bucket

    def write_csv(self, df: pd.DataFrame, path: str):
        wr.s3.to_csv(df=df, path=f"s3://{self.bucket}/{path}", index=False)

    def read_csv(self, path: str) -> pd.DataFrame:
        return wr.s3.read_csv(
            path=f"s3://{self.bucket}/{path}",
        )

    def write_parquet(self, df: pd.DataFrame, path: str):
        wr.s3.to_parquet(
            df=df,
            compression="snappy",
            path=f"s3://{self.bucket}/{path}",
        )

    def create_parquet_path(self, name: str) -> str:
        timestamp = datetime.utcnow()
        path = f"Source=blizzard/\
                DataSet=auctionhouse/\
                Table={name}/\
                IngestionDate={timestamp.strftime('%Y-%m-%d')}/\
                IngestionTimestamp={timestamp.strftime('%Y-%m-%dT%H:%M:%S')}/\
                {name}_{timestamp.strftime('%Y-%m-%dT%H:%M:%S')}.parquet"
        path = path.replace(" ", "")
        return path
