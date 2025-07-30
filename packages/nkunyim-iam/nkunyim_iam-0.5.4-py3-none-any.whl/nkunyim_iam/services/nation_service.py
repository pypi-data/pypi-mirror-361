
from django.http import HttpRequest

from nkunyim_iam.dtos.nation_model import NationModel
from nkunyim_iam.caches.nation_cache import NationCache
from nkunyim_iam.http.http_session import HttpSession



class NationService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
        
    def get(self, code: str) -> NationModel:
        key = f"nat.{self.sess.get_session_key()}"
        cache_manager = NationCache()
        nation = cache_manager.get_nation(key=key)
        if not nation:
            nation = NationModel(req=self.req, code=code.upper())
            cache_manager.set_nation(key=key, nation_data=nation, timeout=60 * 60 * 24)
            
        nat_data = {
            'id': nation.id,
            'code': nation.code,
            'name': nation.name
        }
        self.sess.set_nat(data=nat_data)
        
        return nation
        
