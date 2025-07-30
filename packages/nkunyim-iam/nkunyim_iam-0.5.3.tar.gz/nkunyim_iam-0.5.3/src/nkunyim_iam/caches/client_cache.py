from typing import Union
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from nkunyim_iam.dtos.client_model import ClientModel

from .cache_manager import CacheManager


    
class ClientCache:
    """
    A cache manager for client caching.
    """

    def __init__(self) -> None:
        """
        Initialize the Client Cache with the client cache alias.
        """
        self.cache = CacheManager(settings.CLIENT_CACHE if hasattr(settings, 'CLIENT_CACHE') else DEFAULT_CACHE_ALIAS)
        
    def set_client(self, key: str, client_data: ClientModel, timeout: int = 60 * 60 * 24):
        """
        Set client data in the cache.
        :param key: The key under which the client data is stored.
        :param client: The client data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=client_data, timeout=timeout)
        
    def get_client(self, key: str) -> Union[ClientModel, None]:
        """
        Get client data from the cache.
        :param key: The key of the cached client data.
        :return: The cached client data or None if not found.
        """
        return self.cache.get(key=key)
    
    def delete_client(self, key: str) -> None:
        """
        Delete client data from the cache.
        
        :param key: The key of the cached client data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_clients(self) -> None:
        """
        Clear all client data from the cache.
        """
        self.cache.clear()

   