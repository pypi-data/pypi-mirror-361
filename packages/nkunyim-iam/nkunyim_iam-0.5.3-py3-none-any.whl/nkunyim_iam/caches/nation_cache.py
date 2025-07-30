from typing import Union
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from nkunyim_iam.dtos.nation_model import NationModel

from .cache_manager import CacheManager


    
class NationCache:
    """
    A cache manager for nation caching.
    """

    def __init__(self) -> None:
        """
        Initialize the NaTion Cache with the nation cache alias.
        """
        self.cache = CacheManager(settings.NATION_CACHE if hasattr(settings, 'NATION_CACHE') else DEFAULT_CACHE_ALIAS)
        
    def set_nation(self, key: str, nation_data: NationModel, timeout: int = 60 * 60 * 24):
        """
        Set nation data in the cache.
        :param key: The key under which the nation data is stored.
        :param nation: The nation data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=nation_data, timeout=timeout)
        
    def get_nation(self, key: str) -> Union[NationModel, None]:
        """
        Get nation data from the cache.
        :param key: The key of the cached nation data.
        :return: The cached nation data or None if not found.
        """
        return self.cache.get(key=key)
    
    def delete_nation(self, key: str) -> None:
        """
        Delete nation data from the cache.
        
        :param key: The key of the cached nation data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_nations(self) -> None:
        """
        Clear all nation data from the cache.
        """
        self.cache.clear()