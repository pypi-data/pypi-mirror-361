
from django.http import HttpRequest

from nkunyim_iam.caches.user_agent_cache import UserAgentCache
from nkunyim_iam.http.http_session import HttpSession
from nkunyim_iam.dtos.user_agent_model import UserAgentModel



class UserAgentService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
    
    def get(self) -> UserAgentModel:
        key = f"ua.{self.sess.get_session_key()}"
        cache_manager = UserAgentCache()
        user_agent = cache_manager.get_user_agent(key=key)
        if not user_agent:
            user_agent = UserAgentModel(req=self.req)
            cache_manager.set_user_agent(key=key, user_agent_data=user_agent, timeout=60 * 60 * 24)
            
        return user_agent