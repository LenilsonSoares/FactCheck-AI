import requests
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class GoogleFactCheckClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_urls = [
            "https://factchecktools.googleapis.com/v1alpha1",
            "https://factchecktools.googleapis.com/v1",
        ]

    def search(self, query: str) -> Optional[dict]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY não configurada")

        params = {"query": query, "key": self.api_key}
        last_error = None
        for base_url in self.base_urls:
            url = f"{base_url}/claims:search"
            try:
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if "claims" in data and len(data["claims"]) > 0:
                    return data["claims"][0]
                return None
            except requests.HTTPError as exc:
                # 404 can happen when a given API version/path is unavailable; try next candidate.
                if exc.response is not None and exc.response.status_code == 404:
                    last_error = exc
                    continue
                raise

        if last_error:
            raise last_error

        return None
