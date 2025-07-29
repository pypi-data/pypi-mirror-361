import os

from planqk.api.sdk import PlanqkApi
from planqk.api.sdk.data_pools.client import DataPoolsClient

_PLANQK_API_BASE_URL_NAME = "PLANQK_API_BASE_URL"
_PLANQK_PERSONAL_ACCESS_TOKEN_NAME = "PLANQK_PERSONAL_ACCESS_TOKEN"


class PlanqkApiClient:
    def __init__(self):
        base_url = os.environ.get(_PLANQK_API_BASE_URL_NAME, "https://platform.planqk.de/qc-catalog")
        access_token = os.environ.get(_PLANQK_PERSONAL_ACCESS_TOKEN_NAME)
        self._api = PlanqkApi(base_url=base_url, api_key=access_token)

    @property
    def data_pools(self) -> DataPoolsClient:
        return self._api.data_pools
