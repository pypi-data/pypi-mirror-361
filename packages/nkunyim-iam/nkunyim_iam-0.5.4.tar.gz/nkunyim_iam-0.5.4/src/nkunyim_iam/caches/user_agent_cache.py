from typing import Union
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from nkunyim_iam.dtos.user_agent_model import UserAgentModel

from .cache_manager import CacheManager


class UserAgentCache:
    """
    A cache manager specifically for user agent data.
    """

    def __init__(self) -> None:
        """
        Initialize the UserAgentCache with the user agents cache alias.
        """
        self.cache = CacheManager(settings.USER_AGENTS_CACHE if hasattr(settings, 'USER_AGENTS_CACHE') else DEFAULT_CACHE_ALIAS)    
        
    def set_user_agent(self, key: str, user_agent_data: UserAgentModel, timeout: int = 60 * 60 * 24):
        """
        Set user agent data in the cache.
        
        :param key: The key under which the user agent data is stored.
        :param user_agent_data: The user agent data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=user_agent_data, timeout=timeout)
        
    def get_user_agent(self, key: str) -> Union[UserAgentModel, None]:
        """
        Get user agent data from the cache.
        :param key: The key of the cached user agent data.
        :return: The cached user agent data or None if not found.
        """
        return self.cache.get(key=key)
    
    
    def delete_user_agent(self, key: str) -> None:
        """
        Delete user agent data from the cache.
        
        :param key: The key of the cached user agent data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_user_agents(self) -> None:
        """ 
        Clear all user agent data from the cache.
        """
        self.cache.clear()
        
     