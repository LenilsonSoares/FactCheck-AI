import requests
import os
from typing import Optional


class GoogleFactCheckClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://factchecktools.googleapis.com/v1"

    def search(self, query: str) -> Optional[dict]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY não configurada")

        params = {"query": query, "key": self.api_key}
        url = f"{self.base_url}/claims:search"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "claims" in data and len(data["claims"]) > 0:
            return data["claims"][0]
        return None
