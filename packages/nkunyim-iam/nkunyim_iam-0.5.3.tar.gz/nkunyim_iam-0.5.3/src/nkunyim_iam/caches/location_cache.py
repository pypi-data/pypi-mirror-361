from typing import Union
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from nkunyim_iam.dtos.location_model import LocationModel

from .cache_manager import CacheManager
  

   
class LocationCache:
    """
    A cache manager for location caching.
    """

    def __init__(self) -> None:
        """
        Initialize the Location Cache with the location cache alias.
        """
        self.cache = CacheManager(settings.LOCATION_CACHE if hasattr(settings, 'LOCATION_CACHE') else DEFAULT_CACHE_ALIAS)
        
    def set_location(self, key: str, location_data: LocationModel, timeout: int = 60 * 60 * 24):
        """
        Set location data in the cache.
        :param key: The key under which the location data is stored.
        :param location: The location data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=location_data, timeout=timeout)
        
    def get_location(self, key: str) -> Union[LocationModel, None]:
        """
        Get location data from the cache.
        :param key: The key of the cached location data.
        :return: The cached location data or None if not found.
        """
        return self.cache.get(key=key)
    
    def delete_location(self, key: str) -> None:
        """
        Delete location data from the cache.
        
        :param key: The key of the cached location data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_locations(self) -> None:
        """
        Clear all location data from the cache.
        """
        self.cache.clear()
        
      