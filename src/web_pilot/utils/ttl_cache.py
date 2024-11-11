import pydantic as pyd
import cachetools

from typing import Union
from web_pilot.schemas.constants.cache import CacheProvider
from web_pilot.config import config as conf


class TTLCache:
    def __init__(self) -> None:
        self._cache = self._init_cache(max_items=conf.max_cached_items, ttl=conf.cache_ttl)

    def _init_cache(self, max_items: int = None, ttl: int = None) -> Union[cachetools.TTLCache]:
        if self._provider is None:
            match conf.cache_provider:
                case CacheProvider.IN_MEMORY:
                    self._provider = cachetools.TTLCache(maxsize=max_items, ttl=ttl)
                case _:
                    raise ValueError("Unknown cache provider")
        return self._provider

    def len(self) -> int:
        return len(self._cache)

    def get_item(self, key: str):
        return self._cache.__getitem__(key)

    def set_item(self, key: str, value: pyd.BaseModel) -> None:
        self._cache.__setitem__(key, value)

    def delete_item(self, key: str) -> None:
        self._cache.__delitem__(key)
