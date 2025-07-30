
from django.http import HttpRequest

from nkunyim_iam.dtos.client_model import ClientModel
from nkunyim_iam.caches.client_cache import ClientCache
from nkunyim_iam.http.http_session import HttpSession


class ClientService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
        
    def get(self) -> ClientModel:
        key = f"app.{self.sess.get_session_key()}"
        cache_manager = ClientCache()
        client = cache_manager.get_client(key=key)
        if not client:
            client = ClientModel(req=self.req)
            cache_manager.set_client(key=key, client_data=client, timeout=60 * 60 * 24)
            
        nat_data = {
            'id': client.id,
            'client_id': client.client_id,
            'name': client.name,
            'title': client.title,
        }
        self.sess.set_nat(data=nat_data)
        
        return client
    