from datetime import datetime, timezone, timedelta
from time import sleep
from requests import post


class RandomOrgApi:
    api_key: str
    last_random_org_api_call: datetime | None = None
    min_wait = timedelta(milliseconds=100)

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_true_random_integers(self, n: int, min: int, max: int) -> set[int]:
        # simple rate limiting:
        # max. 10 requests / sec -> ensure waiting min. 100ms between API calls
        if self.last_random_org_api_call is not None:
            elapsed = datetime.now(timezone.utc) - self.last_random_org_api_call
            if elapsed < self.min_wait:
                remaining = self.min_wait - elapsed
                sleep(remaining.total_seconds())

        self.last_random_org_api_call = datetime.now(timezone.utc)

        response = post(
            "https://api.random.org/json-rpc/4/invoke",
            json={
                "id": "",
                "jsonrpc": "2.0",
                "method": "generateIntegerSequences",
                "params": {
                    "apiKey": self.api_key,
                    "n": 1,
                    "length": n,
                    "min": min,
                    "max": max,
                    "replacement": False,
                },
            },
        ).json()

        if "result" in response:
            return set(response["result"]["random"]["data"][0])
        else:
            raise RuntimeError(f"random.org API error: {response['error']['message']}")
