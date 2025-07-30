
from django.http import HttpRequest

from nkunyim_iam.caches.location_cache import LocationCache
from nkunyim_iam.dtos.location_model import LocationModel
from nkunyim_iam.http.http_session import HttpSession



 

class LocationService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
    
    def get(self) -> LocationModel:
        key = f"loc.{self.sess.get_session_key()}"
        cache_manager = LocationCache()
        location = cache_manager.get_location(key=key)
        if not location:
            location = LocationModel(req=self.req)
            cache_manager.set_location(key=key, location_data=location, timeout=60 * 60 * 24)
            
        return location
    
    