import requests
import pandas as pd
import io
from .exceptions import VesselMatchError

class VesselMatch:
    def __init__(self, token: str, base_url: str = "https://api.vesselmatch.com"):
        self.token = token
        self.base_url = base_url.rstrip("/")

    def enrich(self, df: pd.DataFrame, top_k: int = 5, min_score: float = 0.9) -> pd.DataFrame:
        if "vessel_name" not in df.columns:
            raise VesselMatchError("Input DataFrame must have a 'vessel_name' column")

        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        files = {
            "file": ("vessels.parquet", buffer, "application/octet-stream")
        }
        headers = {
            "accept": "application/json",
            "api-token": self.token
        }

        url = f"https://dev.filingsinsight.com/api/shipping/vessel_search_parquet?top_k={top_k}&min_score={min_score}"
        response = requests.post(url, headers=headers, files=files)

        if response.status_code != 200:
            raise VesselMatchError(f"API error: {response.status_code} - {response.text}")

        enriched_buffer = io.BytesIO(response.content)
        return pd.read_parquet(enriched_buffer)
